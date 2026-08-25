# Copyright 2026 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from openupgradelib import openupgrade


def stock_move_account_move_id(env):
    """
    Fill stock.move#account_move_id from account.move#stock_move_id
    """
    env.cr.execute(
        """
        UPDATE stock_move
        SET account_move_id=account_move.id
        FROM account_move
        WHERE
        account_move.stock_move_id=stock_move.id
        AND stock_move.account_move_id IS NULL
        """
    )


def product_category_property_valuation(env):
    """
    Change value 'manual_periodic' to 'periodic'
    """
    env["ir.default"].search(
        [
            ("field_id.name", "=", "property_valuation"),
            ("field_id.model_id.model", "=", "product.category"),
            ("json_value", "=", '"manual_periodic"'),
        ]
    ).write({"json_value": '"periodic"'})

    for company in env["res.company"].search([]):
        env.cr.execute(
            f"""
            UPDATE product_category
            SET
            property_valuation = property_valuation || '{{"{company.id}": "periodic"}}'
            WHERE
            property_valuation->>'{company.id}' = 'manual_periodic'
            """
        )


def stock_location_valuation_account_id(env):
    """
    Set stock.location#valuation_account_id from valuation_in_account_id and
    valuation_out_account_id if they are the same
    """
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE stock_location
        SET valuation_account_id=valuation_in_account_id
        WHERE
        valuation_in_account_id=valuation_out_account_id
        """,
    )


def stock_move_value(env):
    """
    Set stock.move#value to sum of product.value#value for this move
    """
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE stock_move
        SET value=aggregated_values.agg_value
        FROM (
            SELECT
            stock_move_id, sum(value) AS agg_value
            FROM
            stock_valuation_layer
            GROUP BY stock_move_id
        ) aggregated_values
        WHERE aggregated_values.stock_move_id=stock_move.id
        """,
    )


def product_value(env):
    """
    Fill product.value with stock valuations not assigned to a move
    (=manual valuations)
    """
    env.cr.execute(
        """
        ALTER TABLE product_value
        ADD COLUMN IF NOT EXISTS stock_valuation_layer_id int
        """,
    )
    # simple case: the valuation layer has unit_cost set
    env.cr.execute(
        """
        INSERT INTO product_value
        (
            create_uid, create_date, write_uid, write_date, date, lot_id,
            product_id, user_id, value, company_id, description,
            stock_valuation_layer_id
        )
        SELECT
            create_uid, create_date, write_uid, write_date, create_date, lot_id,
            product_id, create_uid, unit_cost, company_id, description,
            id
        FROM stock_valuation_layer
        WHERE
            stock_move_id IS NULL
            AND
            unit_cost IS NOT NULL
        """,
    )
    # otherwise: compute unit cost from sum of all previous values/sum of quantities
    env.cr.execute(
        """
        INSERT INTO product_value
        (
            create_uid, create_date, write_uid, write_date,
            date, lot_id, product_id, user_id,
            company_id, description, value,
            stock_valuation_layer_id
        )
        SELECT
            svl1.create_uid, svl1.create_date, svl1.write_uid, svl1.write_date,
            svl1.create_date, svl1.lot_id, svl1.product_id, svl1.create_uid,
            svl1.company_id, svl1.description, SUM(svl2.value) / SUM(svl2.quantity),
            svl1.id
        FROM stock_valuation_layer svl1
        JOIN stock_valuation_layer svl2
        ON
            svl1.product_id=svl2.product_id
            AND
            svl1.company_id=svl2.company_id
            AND
            (
                svl1.lot_id=svl2.lot_id
                OR svl1.lot_id IS NULL AND svl2.lot_id IS NULL
            )
            AND
            svl1.create_date >= svl2.create_date
        WHERE
            svl1.stock_move_id IS NULL
            AND
            svl1.unit_cost IS NULL
            AND
            svl1.quantity = 0
        GROUP BY
            svl1.id
        HAVING
            SUM(svl2.quantity) <> 0
        """,
    )
    openupgrade.lift_constraints(env.cr, "stock_valuation_layer", "id", cascade=True)


@openupgrade.migrate()
def migrate(env, version):
    stock_move_account_move_id(env)
    product_category_property_valuation(env)
    stock_location_valuation_account_id(env)
    stock_move_value(env)
    product_value(env)
