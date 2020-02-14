# Copyright 2020 ForgeFlow <http://www.forgeflow.com>
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


@openupgrade.migrate()
def migrate(env, version):
    fill_account_move_line_is_landed_costs_line(env)
    openupgrade.load_data(
        env.cr, "stock_landed_costs",
        "migrations/13.0.1.1/noupdate_changes.xml")
