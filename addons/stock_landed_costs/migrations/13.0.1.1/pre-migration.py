# Copyright 2020 ForgeFlow <http://www.forgeflow.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade


def fix_price_unit_of_stock_move(env):
    # in v13 price_unit of stock.move exclude landed_cost_value
    openupgrade.logged_query(
        env.cr, """
        UPDATE stock_move
        SET price_unit = (value - landed_cost_value) / product_qty
        WHERE landed_cost_value != 0.0
        """,
    )


@openupgrade.migrate()
def migrate(env, version):
    fix_price_unit_of_stock_move(env)
