# Copyright 2021 ForgeFlow S.L.  <https://www.forgeflow.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade


def fill_purchase_order_line_qty_to_invoice(env):
    if not openupgrade.column_exists(env.cr, "purchase_order_line", "qty_to_invoice"):
        openupgrade.logged_query(
            env.cr,
            """
            ALTER TABLE purchase_order_line
            ADD COLUMN qty_to_invoice numeric""",
        )
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE purchase_order_line pol
        SET qty_to_invoice = CASE WHEN po.state IN ('purchase', 'done')
            AND pt.purchase_method = 'purchase'
                THEN pol.product_qty - pol.qty_invoiced
            WHEN po.state IN ('purchase', 'done')
                THEN pol.qty_received - pol.qty_invoiced
            ELSE 0 END
        FROM purchase_order po, product_product pp
        JOIN product_template pt ON pp.product_tmpl_id = pt.id
        WHERE pol.order_id = po.id AND pol.product_id = pp.id""",
    )


@openupgrade.migrate()
def migrate(env, version):
    fill_purchase_order_line_qty_to_invoice(env)
