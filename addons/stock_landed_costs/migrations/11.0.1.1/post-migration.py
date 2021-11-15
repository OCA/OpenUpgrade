# Copyright 2021 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade


def fill_stock_move_landed_cost_value(env):
    """Increase stock.move price_unit + fill this field with the sum of
    stock.valuation.adjustment.lines records.
    """
    openupgrade.logged_query(
        env.cr, """
        UPDATE stock_move sm
        SET landed_cost_value = sub.landed_cost,
            price_unit = price_unit + sub.landed_cost
        FROM (
            SELECT SUM(additional_landed_cost) AS landed_cost, move_id
            FROM stock_valuation_adjustment_lines
            GROUP BY move_id
        ) sub
        WHERE sub.move_id = sm.id AND sub.landed_cost != 0
        """
    )


@openupgrade.migrate(use_env=True)
def migrate(env, version):
    fill_stock_move_landed_cost_value(env)
