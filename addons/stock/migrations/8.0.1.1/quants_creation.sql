DROP FUNCTION IF EXISTS float_round(amount float, rounding float, rounding_method varchar);
CREATE OR REPLACE FUNCTION float_round(amount float, rounding float, rounding_method varchar)
RETURNS float AS $$
    DECLARE
        normalized_value float;
        epsilon_magnitude float;
        epsilon float;
        rounded_value float;
        sign float;
    BEGIN
        IF amount = 0.0 THEN
            RETURN amount;
        END IF;
        IF rounding_method is null THEN
            rounding_method := 'UP';
        END IF;

        normalized_value := amount / rounding;
        epsilon_magnitude := log(abs(normalized_value)) /  log(2);
        epsilon := 2^(epsilon_magnitude-53);
        IF rounding_method = 'HALF-UP' THEN
            CASE WHEN normalized_value < 0 THEN
                sign := -1 * epsilon;
            WHEN normalized_value = 0 THEN
                sign := 0 * epsilon;
            WHEN normalized_value > 0 THEN
                sign := 1 * epsilon;
            END CASE;
            normalized_value := normalized_value + (sign*epsilon);
            rounded_value := round(normalized_value);
        ELSIF rounding_method = 'UP' THEN
            CASE WHEN normalized_value < 0 THEN
                sign := -1;
            WHEN normalized_value = 0 THEN
                sign := 0;
            WHEN normalized_value > 0 THEN
                sign := 1;
            END CASE;
            normalized_value := normalized_value - (sign*epsilon);
            rounded_value := ceil(abs(normalized_value)) * sign;
        END IF;
        amount := rounded_value * rounding;

        RETURN amount;
    END;
    $$ LANGUAGE plpgsql;

DROP FUNCTION IF EXISTS compute_qty_obj(from_uom product_uom, qty float, to_unit product_uom, rounding_method varchar);
CREATE OR REPLACE FUNCTION compute_qty_obj(from_uom product_uom, qty float, to_unit product_uom, rounding_method varchar)
RETURNS float AS $$
    DECLARE
        amount float;
    BEGIN
        IF rounding_method is null THEN
            rounding_method := 'UP';
        END IF;

        IF from_uom.category_id != to_unit.category_id THEN
            RAISE EXCEPTION USING MESSAGE = 'The category of the unit of measure ' || from_uom.name || ' is different to the unit of measure '|| to_unit.name;
        END IF;
        amount := qty / from_uom.factor;
        IF to_unit is not null THEN
            amount := amount * to_unit.factor;
            SELECT float_round(amount, to_unit.rounding, rounding_method) INTO amount;
        END IF;

        RETURN amount;
    END;
    $$ LANGUAGE plpgsql;



DROP FUNCTION IF EXISTS get_child_locations(source_location integer);
CREATE OR REPLACE FUNCTION get_child_locations(source_location integer)
RETURNS integer[] AS $$
    DECLARE
        returned integer[];
    BEGIN
        SELECT array_agg(id) INTO returned
        FROM (WITH RECURSIVE tree AS (
              SELECT id, ARRAY[]::INTEGER[] AS ancestors
              FROM stock_location WHERE location_id IS NULL
              UNION ALL
              SELECT
                stock_location.id,
                tree.ancestors || stock_location.location_id
              FROM
                stock_location, tree
              WHERE
                stock_location.location_id = tree.id
            )
            SELECT
                *
            FROM
                tree
            WHERE
                source_location = ANY(tree.ancestors) OR
                id = source_location) AS a;
        RETURN returned;
    END;
    $$ LANGUAGE plpgsql;


DROP FUNCTION IF EXISTS quants_get(move stock_move, quantity float, where_qty varchar, location integer);
CREATE OR REPLACE FUNCTION quants_get(move stock_move, quantity float, where_qty varchar, location integer)
RETURNS float[] AS $$
    DECLARE
        quant_id integer;
        quant_qty float;
        returned float[];
        locations integer[];
        qry varchar;
    BEGIN
        IF EXISTS (SELECT id FROM stock_location
                   WHERE id=location
                   AND usage in ('inventory', 'production', 'supplier')) THEN
            RETURN array[[null, quantity]];
        END IF;
        SELECT get_child_locations(location) INTO locations;
        qry := ('SELECT id, qty FROM stock_quant '||
                     'WHERE product_id = ' ||move.product_id  ||
                           ' AND location_id = ANY('||quote_literal(locations)||')' ||
                           where_qty ||
                           ' AND company_id = '||move.company_id ||
                        ' ORDER BY in_date ASC');
        FOR quant_id, quant_qty IN EXECUTE qry LOOP

            IF quantity < abs(quant_qty) AND quantity > 0 THEN
                returned := returned || array[[quant_id, quantity]];
                quantity := 0;
                EXIT;

            ELSIF quantity >= abs(quant_qty) AND quantity > 0 THEN
                returned := returned || array[[quant_id, abs(quant_qty)]];
                quantity := quantity - abs(quant_qty);

            ELSIF quantity <= 0 THEN
                EXIT;
            END IF;
        END LOOP;

        IF quantity > 0 THEN
            returned := returned || array[[null, quantity]];
        END IF;


        RETURN returned;
    END;
    $$ LANGUAGE plpgsql;

DROP FUNCTION IF EXISTS create_quant(move stock_move, quantity float);
CREATE OR REPLACE FUNCTION create_quant(move stock_move, quantity float)
RETURNS integer AS $$
    DECLARE
        quant integer;
        negative integer;
        super_admin integer;
    BEGIN
        super_admin := 1;
        negative := null;
        IF EXISTS (SELECT id FROM stock_location
                   WHERE id=move.location_id
                   AND usage='internal') THEN
            INSERT INTO stock_quant (create_date, qty,
                propagated_from_id, package_id, cost, lot_id,
                reservation_id, create_uid, location_id, company_id,
                owner_id,  write_date, write_uid, product_id,
                packaging_type_id, negative_move_id, in_date) VALUES
            (move.write_date, -1 * quantity, null, null,
                move.price_unit, null, null, super_admin,
                move.location_id, move.company_id, null,
                move.write_date, super_admin, move.product_id, null, move.id,
                move.date) RETURNING id INTO negative;
            INSERT INTO stock_quant_move_rel (quant_id, move_id)
                                      VALUES (negative, move.id);
        END IF;

        INSERT INTO stock_quant (create_date, qty,
            propagated_from_id, package_id, cost, lot_id,
            reservation_id, create_uid, location_id, company_id,
            owner_id,  write_date, write_uid, product_id,
            packaging_type_id, negative_move_id, in_date) VALUES
        (move.write_date, quantity, negative, null,
            move.price_unit, null, null, super_admin,
            move.location_dest_id, move.company_id, null,
            move.write_date, super_admin, move.product_id, null, null,
            move.date) RETURNING id INTO quant;

            INSERT INTO stock_quant_move_rel (quant_id, move_id)
                                      VALUES (quant, move.id);

        RETURN quant;
    END;
    $$ LANGUAGE plpgsql;

DROP FUNCTION IF EXISTS quant_split(quant integer, quantity float);
CREATE OR REPLACE FUNCTION quant_split(quant integer, quantity float)
RETURNS integer AS $$
    DECLARE
        uom_rounding float;
        value float;
        value1 float;
        value2 float;
        qty_round float;
        new_qty_round float;
        copy_quant integer;
        cquant stock_quant%rowtype;
    BEGIN
        SELECT * INTO cquant FROM stock_quant WHERE id=quant;
        SELECT
            uom.rounding INTO uom_rounding
        FROM
            product_product AS pro
        INNER JOIN
            product_template AS tem on tem.id = pro.product_tmpl_id
        INNER JOIN
            product_uom AS uom ON uom.id = tem.uom_id
        WHERE
            pro.id = cquant.product_id
        LIMIT 1;

        SELECT float_round(abs(cquant.qty), uom_rounding, 'HALF-UP') INTO value1;
        SELECT float_round(abs(quantity), uom_rounding, 'HALF-UP') INTO value2;
        value := value1 - value2;
        IF value > 0 THEN
            SELECT float_round(quantity, uom_rounding, 'HALF-UP') INTO qty_round;
            SELECT float_round(cquant.qty - quantity, uom_rounding, 'HALF-UP') INTO new_qty_round;
            INSERT INTO stock_quant (create_date, qty,
                propagated_from_id, package_id, cost, lot_id,
                reservation_id, create_uid, location_id, company_id,
                owner_id,  write_date, write_uid, product_id,
                packaging_type_id, negative_move_id, in_date)
            VALUES (cquant.create_date, new_qty_round,
                cquant.propagated_from_id, cquant.package_id,
                cquant.cost, cquant.lot_id,
                cquant.reservation_id, cquant.create_uid,
                cquant.location_id, cquant.company_id,
                cquant.owner_id,  cquant.write_date,
                cquant.write_uid, cquant.product_id,
                cquant.packaging_type_id, cquant.negative_move_id, cquant.in_date
            ) RETURNING id INTO copy_quant;

            INSERT INTO stock_quant_move_rel (quant_id, move_id)
                        (SELECT
                            copy_quant,
                            rel.move_id
                         FROM
                            stock_quant_move_rel AS rel
                         WHERE
                            rel.quant_id=quant);
            UPDATE stock_quant SET qty = qty_round WHERE id = quant;
        END IF;


        RETURN copy_quant;
    END;
    $$ LANGUAGE plpgsql;


DROP FUNCTION IF EXISTS reconcile_negative(quant_rec integer, move stock_move);
CREATE OR REPLACE FUNCTION reconcile_negative(quant_rec integer, move stock_move)
RETURNS integer AS $$
    DECLARE
        quant_to_rec stock_quant%rowtype;
        to_solve_quant stock_quant%rowtype;
        neg_quants float[];
        quant float[];
        solved_quant_ids integer[];
        move_used integer[];
        uom_rounding float;
        solving_qty float;
        value1 float;
        value2 float;
        value float;
        inv_qty float;
        remaining_solving_quant integer;
        remaining_neg_quant integer;
        solving_quant integer;
        solve integer;
        current_quant integer;
        list_quants "stock_quant"[];
    BEGIN
        SELECT
            uom.rounding INTO uom_rounding
        FROM
            product_product AS pro
        INNER JOIN
            product_template AS tem on tem.id = pro.product_tmpl_id
        INNER JOIN
            product_uom AS uom ON uom.id = tem.uom_id
        WHERE
            pro.id = move.product_id
        LIMIT 1;
        solving_quant := quant_rec;
        SELECT * INTO quant_to_rec FROM stock_quant WHERE id=solving_quant;
        SELECT quants_get(move, quant_to_rec.qty,
                          ' AND qty < 0 AND id != ' || COALESCE(quant_to_rec.propagated_from_id, 0),
                          quant_to_rec.location_id) INTO neg_quants;
        FOREACH quant SLICE 1 IN ARRAY neg_quants LOOP
            IF quant[1] IS NULL OR solving_quant is null THEN
                CONTINUE;
            END IF;
            SELECT array_agg(qua) INTO list_quants FROM stock_quant AS qua WHERE propagated_from_id=quant[1];
            IF list_quants IS NULL THEN
                CONTINUE;
            END IF;
            SELECT * INTO quant_to_rec FROM stock_quant WHERE id=solving_quant;
            current_quant := quant[1];
            solving_qty := quant[2];
            solved_quant_ids := '{}';
            FOREACH to_solve_quant SLICE 0 IN ARRAY list_quants LOOP
                SELECT float_round(solving_qty, uom_rounding, 'HALF-UP') INTO value1;
                value2 := 0;
                value := value1 - value2;
                IF value <= 0 THEN
                    CONTINUE;
                END IF;
                solved_quant_ids := solved_quant_ids || array[to_solve_quant.id];
                PERFORM quant_split(to_solve_quant.id, LEAST(solving_qty, to_solve_quant.qty));
                solving_qty := solving_qty -  LEAST(solving_qty, to_solve_quant.qty);
            END LOOP;
            inv_qty := -1 * quant[2];
            SELECT quant_split(quant_to_rec.id, quant[2]) INTO remaining_solving_quant;
            SELECT quant_split(CAST(quant[1] AS integer), inv_qty) INTO remaining_neg_quant;
            /* if the reconciliation was not complete, we need to link together the remaining parts */
            IF remaining_neg_quant is not null THEN
                UPDATE
                    stock_quant
                SET
                    propagated_from_id=remaining_neg_quant
                WHERE
                    propagated_from_id=quant[1]
                    AND id != ALL(solved_quant_ids);
            END IF;

            IF quant_to_rec.propagated_from_id is not null AND array_length(solved_quant_ids, 1) > 0 THEN
                UPDATE
                    stock_quant
                SET
                    propagated_from_id=quant_to_rec.propagated_from_id
                WHERE
                    id = ANY(solved_quant_ids);
            END IF;
            /* delete the reconciled quants, as it is replaced by the solved quants */
            DELETE FROM stock_quant WHERE id=quant[1];

            IF array_length(solved_quant_ids, 1) > 0 THEN
                /* price update + accounting entries adjustment */
                UPDATE
                    stock_quant
                SET
                    cost=quant_to_rec.cost
                WHERE
                    id = ANY(solved_quant_ids);
                /* merge history (and cost?) */
                SELECT array_agg(move_id) INTO move_used FROM stock_quant_move_rel WHERE quant_id = ANY(solved_quant_ids);
                FOREACH solve SLICE 0 IN ARRAY solved_quant_ids LOOP
                    INSERT INTO stock_quant_move_rel (quant_id, move_id)
                    (SELECT
                        solve,
                        rel.move_id
                     FROM
                        stock_quant_move_rel AS rel
                     WHERE
                        rel.quant_id=quant_to_rec.id
                        AND rel.move_id != ALL(move_used));
                END LOOP;
            END IF;
            DELETE FROM stock_quant WHERE id=quant_to_rec.id;
            solving_quant := remaining_solving_quant;
        END LOOP;

        RETURN solving_quant;
    END;
    $$ LANGUAGE plpgsql;

DROP FUNCTION IF EXISTS quants_move(move stock_move, quants float[]);
CREATE OR REPLACE FUNCTION quants_move(move stock_move, quants float[])
RETURNS integer[] AS $$
    DECLARE
        quants_reconcile integer[];
        quant float[];
        current_quant integer;
        recon_quant integer;
        locations integer[];
    BEGIN
        FOREACH quant SLICE 1 IN ARRAY quants LOOP
            current_quant := quant[1];
            IF quant[1] is null THEN
                SELECT create_quant(move, quant[2]) INTO current_quant;
            ELSE
                PERFORM quant_split(CAST(quant[1] AS integer), quant[2]);
                UPDATE
                    stock_quant
                SET
                    location_id=move.location_dest_id
                WHERE
                    id = current_quant;
                INSERT INTO stock_quant_move_rel (quant_id, move_id)
                                          VALUES (current_quant, move.id);
            END IF;
            quants_reconcile := quants_reconcile || array[current_quant];
        END LOOP;
            IF EXISTS (SELECT
                           id
                       FROM
                           stock_location
                       WHERE
                           id = move.location_dest_id
                           AND usage = 'internal') THEN
                SELECT get_child_locations(move.location_dest_id) INTO locations;
                IF EXISTS (SELECT 1
                           FROM
                               stock_quant
                           WHERE
                               qty < 0
                               AND product_id = move.product_id
                               AND company_id = move.company_id
                               AND location_id = ANY(locations) LIMIT 1) THEN
                    FOREACH recon_quant IN ARRAY quants_reconcile LOOP
                        PERFORM reconcile_negative(recon_quant, move);
                    END LOOP;

                END IF;
            END IF;

        RETURN quants_reconcile;
    END;
    $$ LANGUAGE plpgsql;

-- Create a Log table that will be populated if the
-- treatment of a move fail.
DROP TABLE IF EXISTS stock_quants_openupgrade_8_log;

CREATE TABLE stock_quants_openupgrade_8_log(
    stock_move_id integer NOT NULL,
    sql_code character varying NOT NULL,
    sql_message text
);

-- Main Function
DROP FUNCTION IF EXISTS action_done();
CREATE OR REPLACE FUNCTION action_done()
RETURNS integer AS $$
    DECLARE
        error_qty integer;
        quants_used integer[];
        quants_to_use float[];
        from_uom product_uom%rowtype;
        to_uom product_uom%rowtype;
        move stock_move%rowtype;
        template integer;
        current_qty float;
    BEGIN
        error_qty := 0;
        FOR move IN SELECT * FROM stock_move WHERE state='done' AND product_uom_qty > 0 ORDER BY date ASC LOOP
            BEGIN
                template := (SELECT product_tmpl_id FROM product_product WHERE id=move.product_id);
                SELECT * INTO from_uom FROM product_uom WHERE id=move.product_uom;
                SELECT * INTO to_uom FROM product_uom WHERE id IN (SELECT uom_id FROM product_template WHERE id = template);
                SELECT compute_qty_obj(from_uom, move.product_uom_qty, to_uom, 'HALF-UP') INTO current_qty;
                SELECT quants_get(move, current_qty, ' AND qty > 0', move.location_id) INTO quants_to_use;
                SELECT quants_move(move, quants_to_use) INTO quants_used;

            EXCEPTION WHEN others THEN
                error_qty := error_qty +1;
                INSERT INTO stock_quants_openupgrade_8_log(stock_move_id, sql_code, sql_message)
                    VALUES (move.id, SQLSTATE, SQLERRM);

            END;
        END LOOP;
        RETURN error_qty;
    END;
    $$ LANGUAGE plpgsql;

SELECT action_done();
