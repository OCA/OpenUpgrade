# Copyright 2020 ForgeFlow <http://www.forgeflow.com>
# Copyright 2021 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade


def fix_purchase_order_line_propagate_cancel(env):
    openupgrade.logged_query(
        env.cr, """
        UPDATE purchase_order_line pol
        SET propagate_cancel = FALSE
        FROM stock_move sm
        WHERE sm.purchase_line_id = pol.id AND NOT sm.propagate_cancel"""
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


def fill_purchase_order_line__qty_received_method(env):
    """Set qty_delivered_method = 'stock_moves' on proper lines."""
    openupgrade.logged_query(
        env.cr, """
        UPDATE purchase_order_line pol
        SET qty_received_method = 'stock_moves', qty_received_manual = 0
        FROM product_product pp
        LEFT JOIN product_template pt ON pp.product_tmpl_id = pt.id
        WHERE pol.product_id = pp.id AND pol.display_type IS NULL
            AND pt.type IN ('consu', 'product')"""
    )


@openupgrade.migrate()
def migrate(env, version):
    fix_purchase_order_line_propagate_cancel(env)
    fill_propagate_date_minimum_delta(env)
    fill_purchase_order_line__qty_received_method(env)
