# Copyright 2025 ForgeFlow S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from openupgradelib import openupgrade

_new_columns = [
    ("purchase.order.line", "group_id", "many2one"),
    ("purchase.order.line", "location_final_id", "many2one"),
    ("stock.warehouse.orderpoint", "product_supplier_id", "many2one"),
]


def fill_purchase_order_line_group_id(env):
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE purchase_order_line pol
        SET group_id = sr.group_id
        FROM stock_move sm
        JOIN stock_rule sr ON sm.rule_id = sr.id AND
            sr.group_propagation_option = 'propagate'
        WHERE sm.purchase_line_id = pol.id
            AND pol.group_id IS NULL AND sr.group_id IS NOT NULL
        """,
    )
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE purchase_order_line pol
        SET group_id = po.group_id
        FROM purchase_order po
        JOIN stock_rule sr ON po.group_id = sr.group_id AND
            sr.group_propagation_option = 'propagate'
        WHERE pol.order_id = po.id AND pol.group_id IS NULL
        """,
    )
    if openupgrade.column_exists(env.cr, "purchase_order_line", "sale_line_id"):
        openupgrade.logged_query(
            env.cr,
            """
            UPDATE purchase_order_line pol
            SET group_id = pg.id
            FROM sale_order_line sol
            JOIN procurement_group pg ON pg.sale_id = sol.order_id
            JOIN stock_rule sr ON pg.id = sr.group_id AND
                sr.group_propagation_option = 'propagate'
            WHERE pol.sale_line_id = sol.id AND pol.group_id IS NULL
            """,
        )
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE purchase_order_line pol
        SET group_id = sm.group_id
        FROM stock_move sm
        WHERE sm.purchase_line_id = pol.id AND pol.group_id IS NULL
        """,
    )


def fill_purchase_order_line_location_final_id(env):
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE purchase_order_line pol
        SET location_final_id = sm.location_final_id
        FROM stock_move sm
        WHERE sm.purchase_line_id = pol.id
        """,
    )


def fill_stock_warehouse_orderpoint_product_supplier_id(env):
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE stock_warehouse_orderpoint swo
        SET product_supplier_id = sub.partner_id
        FROM product_product pp
        JOIN product_template pt ON pp.product_tmpl_id = pt.id
        JOIN LATERAL (
            SELECT ps.partner_id
            FROM product_supplierinfo ps
            WHERE ps.product_tmpl_id = pt.id
            ORDER BY ps.sequence
            LIMIT 1
        ) sub ON TRUE
        WHERE swo.product_id = pp.id
        """,
    )


@openupgrade.migrate()
def migrate(env, version=None):
    openupgrade.add_columns(env, _new_columns)
    fill_purchase_order_line_group_id(env)
    fill_purchase_order_line_location_final_id(env)
    fill_stock_warehouse_orderpoint_product_supplier_id(env)
