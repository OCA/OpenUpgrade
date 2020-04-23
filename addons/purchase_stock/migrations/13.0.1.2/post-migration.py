# Copyright 2020 ForgeFlow <http://www.forgeflow.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade


def fix_purchase_order_line_propagate_cancel(env):
    openupgrade.logged_query(
        env.cr, """
        UPDATE purchase_order_line pol
        SET propagate_cancel = FALSE
        FROM stock_move sm
        WHERE sm.purchase_line_id = pol.id AND sm.propagate_cancel = FALSE
        """
    )


def fill_propagate_date_minimum_delta(env):
    # purchase order line
    openupgrade.logged_query(
        env.cr, """
        UPDATE purchase_order_line pol
        SET propagate_date_minimum_delta = rc.propagation_minimum_delta
        FROM res_company rc
        WHERE pol.company_id = rc.id AND
            pol.propagate_date_minimum_delta IS NULL
            AND rc.propagation_minimum_delta IS NOT NULL
        """
    )
    openupgrade.logged_query(
        env.cr, """
        UPDATE purchase_order_line pol
        SET propagate_date = TRUE
        FROM ir_config_parameter icp
        WHERE pol.propagate_date IS NULL
            AND icp.key = 'stock.use_propagation_minimum_delta'
            AND icp.value = 'True'
        """
    )


@openupgrade.migrate()
def migrate(env, version):
    fix_purchase_order_line_propagate_cancel(env)
    fill_propagate_date_minimum_delta(env)
