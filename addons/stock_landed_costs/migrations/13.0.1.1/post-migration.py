# Copyright 2020 ForgeFlow <http://www.forgeflow.com>
# Copyright 2021 Andrii Skrypka
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade


def fill_account_move_line_is_landed_costs_line(env):
    openupgrade.logged_query(
        env.cr, """
        UPDATE account_move_line aml
        SET is_landed_costs_line = TRUE
        FROM product_product pp
        JOIN product_template pt ON pp.product_tmpl_id = pt.id
        WHERE aml.product_id = pp.id
            AND pt.landed_cost_ok AND pt.type = 'service'""",
    )


def _generate_stock_valuation_layer(env):
    """Insert a svl record per landed cost line, indicating the cost."""
    openupgrade.logged_query(
        env.cr, """
        INSERT INTO stock_valuation_layer (value, unit_cost, quantity, remaining_qty,
            stock_valuation_layer_id, description, stock_move_id, product_id,
            stock_landed_cost_id, company_id, account_move_id, create_date, create_uid,
            write_date, write_uid)
        SELECT sval.additional_landed_cost, 0.0, 0.0, 0.0,
            svl.id, slc.name, sm.id, sm.product_id,
            slc.id, am.company_id, am.id, am.create_date, am.create_uid,
            am.write_date, am.write_uid
        FROM stock_landed_cost slc
        JOIN account_move am ON am.id = slc.account_move_id
        JOIN stock_valuation_adjustment_lines sval ON sval.cost_id = slc.id
        JOIN stock_move sm ON sm.id = sval.move_id
        LEFT JOIN (
            SELECT MIN(id) as id, stock_move_id
            FROM stock_valuation_layer
            GROUP BY stock_move_id
        ) svl ON svl.stock_move_id = sval.move_id
        WHERE slc.state = 'done'
        """,
    )


def _fix_value_for_svl(env):
    """As previous stock move price unit contains the landed cost price, the
    svl were created counting with this price, so we have to substract it now.
    """
    openupgrade.logged_query(
        env.cr, """
        UPDATE stock_valuation_layer svl
        SET value = svl.value - svl_value.diff
        FROM (
            SELECT stock_valuation_layer_id as id, SUM(value) as diff
            FROM stock_valuation_layer
            WHERE stock_valuation_layer_id IS NOT NULL
            GROUP BY stock_valuation_layer_id
        ) svl_value
        WHERE svl_value.id = svl.id
        """,
    )


@openupgrade.migrate()
def migrate(env, version):
    fill_account_move_line_is_landed_costs_line(env)
    openupgrade.load_data(
        env.cr, "stock_landed_costs",
        "migrations/13.0.1.1/noupdate_changes.xml")
    _generate_stock_valuation_layer(env)
    _fix_value_for_svl(env)
