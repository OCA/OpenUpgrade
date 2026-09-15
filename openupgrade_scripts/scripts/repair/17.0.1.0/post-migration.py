# Copyright 2025 ForgeFlow S.L. (https://www.forgeflow.com)
# Copyright 2025 Tecnativa - Carlos Lopez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade


def fill_product_template_create_repair(env):
    # If fees where created for some service,
    # they should create repair orders automatically
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE product_template pt
        SET create_repair = TRUE
        FROM repair_fee rf
        JOIN product_product pp ON rf.product_id = pp.id
        WHERE pp.product_tmpl_id = pt.id""",
    )


def fill_stock_move_repair_line_type(env):
    # Set the repair_line_type in stock moves
    # to link them to the repair order through the move_ids field.
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE stock_move sm
        SET repair_line_type = rl.type,
            description_picking = rl.name
        FROM repair_line rl
        WHERE rl.move_id = sm.id
        """,
    )


def fill_stock_move_repair_lines_in_process(env):
    """
    Insert moves for repairs lines not done yet
    - Set the default values for the new fields, as defined in the field declarations.
    - Set the state according to the repair's state to maintain consistency.
    - Set the quantity to 0 because in V16
        the reservation is not done until the repair is completed,
        so no reservation should be made on the stock move.
    """
    openupgrade.logged_query(
        env.cr,
        """
        INSERT INTO stock_move (
            old_repair_line_id,
            sequence, priority,
            propagate_cancel,
            additional,
            picked,
            create_uid, create_date, write_uid, write_date,
            repair_id, repair_line_type,
            picking_type_id, location_id, location_dest_id,
            product_id, product_uom,
            product_uom_qty, product_qty, quantity,
            name, description_picking,
            date, company_id,
            origin, reference,
            procure_method,
            scrapped,
            state
        )
        SELECT rl.id,
            10 AS sequence, '0' AS priority,
            true AS propagate_cancel,
            false AS additional,
            false AS picked,
            rl.create_uid, rl.create_date, rl.write_uid, rl.write_date,
            rl.repair_id, rl.type AS repair_line_type,
            ro.picking_type_id, rl.location_id, rl.location_dest_id,
            rl.product_id, rl.product_uom,
            rl.product_uom_qty,
            ROUND(
                ((rl.product_uom_qty / rl_uom.factor) * pt_uom.factor),
                SCALE(pt_uom.rounding)
                ) AS product_qty,
            0 AS quantity,
            ro.name, rl.name AS description_picking,
            ro.schedule_date AS date, rl.company_id,
            ro.name AS origin, ro.name AS reference,
            'make_to_stock' AS procure_method,
            sld.scrap_location AS scrapped,
            CASE WHEN ro.state IN ('draft', 'cancel')
                THEN ro.state ELSE 'confirmed'
            END AS state
        FROM repair_line rl
            JOIN repair_order ro ON rl.repair_id = ro.id
            JOIN stock_location sld ON sld.id = rl.location_dest_id
            JOIN product_product pp ON pp.id = rl.product_id
            JOIN product_template pt ON pt.id = pp.product_tmpl_id
            JOIN uom_uom rl_uom ON rl_uom.id = rl.product_uom
            JOIN uom_uom pt_uom ON pt_uom.id = pt.uom_id
        WHERE rl.move_id IS NULL AND rl.type IS NOT NULL
        """,
    )


def create_default_repair_type_for_all_warehouses(env):
    # method mainly based on _create_or_update_sequences_and_picking_types()
    all_warehouses = (
        env["stock.warehouse"]
        .with_context(active_test=False)
        .search([("repair_type_id", "=", False)])
    )
    for wh in all_warehouses:
        # choose the next available color for the operation types of this warehouse
        all_used_colors = [
            res["color"]
            for res in env["stock.picking.type"]
            .with_context(active_test=False)
            .search_read(
                [("warehouse_id", "!=", False), ("color", "!=", False)],
                ["color"],
                order="color",
            )
        ]
        available_colors = [zef for zef in range(0, 12) if zef not in all_used_colors]
        color = available_colors[0] if available_colors else 0
        sequence_data = wh._get_sequence_values()
        # suit for each warehouse: reception, internal, pick, pack, ship
        max_sequence = (
            env["stock.picking.type"]
            .with_context(active_test=False)
            .search_read(
                [("sequence", "!=", False)],
                ["sequence"],
                limit=1,
                order="sequence desc",
            )
        )
        max_sequence = max_sequence and max_sequence[0]["sequence"] or 0
        values = wh._get_picking_type_update_values()["repair_type_id"]
        create_data, _ = wh._get_picking_type_create_values(max_sequence)
        values.update(create_data["repair_type_id"])
        sequence = env["ir.sequence"].create(sequence_data["repair_type_id"])
        values.update(
            warehouse_id=wh.id,
            color=color,
            sequence_id=sequence.id,
            sequence=max_sequence + 1,
            company_id=wh.company_id.id,
            active=wh.active,
        )
        # create repair picking type
        repair_type_id = env["stock.picking.type"].create(values).id
        # update repair picking type for warehouse
        wh.write({"repair_type_id": repair_type_id})


def repair_map_state(env):
    """
    Map the states of the repair orders to the new ones.
    The mapping is as follows:
    - ready -> confirmed. Order not repaired but already invoiced.
        TODO: Decide how to handle the invoice
            when it has been created before the repair is completed.
    - 2binvoiced and not repaired -> confirmed. Order not repaired and not invoiced
    - 2binvoiced and repaired -> done. Order repaired but not invoiced
    """
    state_legacy = openupgrade.get_legacy_name("state")
    openupgrade.map_values(
        env.cr,
        state_legacy,
        "state",
        [("ready", "confirmed")],
        table="repair_order",
    )
    openupgrade.logged_query(
        env.cr,
        f"""
        UPDATE repair_order
        SET state = 'confirmed'
        WHERE {state_legacy} = '2binvoiced' AND (not repaired OR repaired IS NULL)
        """,
    )
    openupgrade.logged_query(
        env.cr,
        f"""
        UPDATE repair_order
        SET state = 'done'
        WHERE {state_legacy} = '2binvoiced' AND repaired
        """,
    )


def fill_repair_picking_type(env):
    """
    Update the picking type of the repair orders
    to the one defined in the warehouse.
    Set the related fields from picking_type_id
    """
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE repair_order ro
        SET picking_type_id = sw.repair_type_id,
            location_dest_id = spt.default_location_dest_id,
            parts_location_id = spt.default_remove_location_dest_id,
            recycle_location_id = spt.default_recycle_location_dest_id
        FROM stock_location sl
            JOIN stock_warehouse sw ON sw.id = sl.warehouse_id
            JOIN stock_picking_type spt ON spt.id = sw.repair_type_id
        WHERE ro.location_id = sl.id
        """,
    )
    # Remove/Archive the temporary location and picking type
    # created during the migration
    temp_location = env["stock.location"].search(
        [("name", "=", "Temporary Location OpenUpgrade")]
    )
    openupgrade.logged_query(
        env.cr,
        """
        SELECT id
        FROM repair_order
        WHERE location_dest_id = %(temp_location_id)s
        OR parts_location_id = %(temp_location_id)s
        OR recycle_location_id = %(temp_location_id)s
        """,
        dict(temp_location_id=temp_location.id),
    )
    if env.cr.fetchone():
        temp_location.write(
            {
                "name": "Historical OpenUpgrade Location for 17.0 migration",
                "active": False,
            }
        )
    else:
        temp_location.unlink()

    temp_type = env["stock.picking.type"].search(
        [("name", "=", "SPT Repair OpenUpgrade")]
    )
    openupgrade.logged_query(
        env.cr,
        """
        SELECT id
        FROM repair_order
        WHERE picking_type_id = %(temp_type_id)s
        """,
        dict(temp_type_id=temp_type.id),
    )
    if env.cr.fetchone():
        temp_type.write(
            {
                "name": "Historical OpenUpgrade Picking Type for 17.0 migration",
                "active": False,
            }
        )
    else:
        temp_type.unlink()


def fill_repair_procurement_group(env):
    """
    Insert the procurement group for the repair orders
    and assign it to the stock moves,
    similar to what is done in the create method of stock.move.
    """
    openupgrade.logged_query(
        env.cr,
        """
        INSERT INTO procurement_group (
            create_uid, create_date, write_uid, write_date,
            name, move_type
        )
        SELECT
            ro.create_uid, ro.create_date, ro.write_uid, ro.write_date,
            ro.name, 'direct' AS move_type
        FROM repair_order ro
        WHERE ro.procurement_group_id IS NULL
        """,
    )
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE repair_order ro
        SET procurement_group_id = pg.id
        FROM procurement_group pg
        WHERE pg.name = ro.name
        """,
    )
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE stock_move sm
        SET group_id = ro.procurement_group_id,
        picking_type_id = ro.picking_type_id
        FROM repair_order ro
        WHERE sm.repair_id = ro.id
        """,
    )


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.load_data(env, "repair", "17.0.1.0/noupdate_changes.xml")
    create_default_repair_type_for_all_warehouses(env)
    # Ensure the repair_type_id field is sent to the database
    # before using this field in SQL queries.
    env["stock.warehouse"].flush_model(["repair_type_id"])
    fill_product_template_create_repair(env)
    fill_stock_move_repair_line_type(env)
    fill_stock_move_repair_lines_in_process(env)
    repair_map_state(env)
    fill_repair_picking_type(env)
    fill_repair_procurement_group(env)
    openupgrade.delete_records_safely_by_xml_id(
        env,
        [
            "repair.repair_fee_rule",
            "repair.repair_line_rule",
            "repair.seq_repair",
            "repair.mail_template_repair_quotation",
        ],
    )
