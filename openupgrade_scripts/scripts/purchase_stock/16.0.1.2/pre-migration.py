from openupgradelib import openupgrade


def _compute_purchase_order_receipt_status(env):
    openupgrade.add_fields(
        env,
        [
            (
                "receipt_status",
                "purchase.order",
                "purchase_order",
                "selection",
                "character varying",
                "purchase_stock",
                False,
            ),
        ],
    )
    openupgrade.logged_query(
        env.cr,
        """
        WITH po_receipt_status as (
            SELECT rel.purchase_order_id as id,
            CASE
                WHEN
                    COUNT(sp.state) FILTER(WHERE sp.state = 'cancel') = COUNT(sp.state)
                    THEN null
                WHEN
                    COUNT(sp.state) FILTER(WHERE sp.state not in ('done', 'cancel')) = 0
                    THEN 'full'
                WHEN
                    COUNT(sp.state) FILTER(WHERE sp.state = 'done') > 0
                    THEN 'partial'
                ELSE 'pending'
            END as receipt_status
            FROM stock_picking as sp
            JOIN purchase_order_stock_picking_rel as rel
                ON rel.stock_picking_id = sp.id
            GROUP BY 1
            ORDER BY 1
        )
        UPDATE purchase_order as po
            SET receipt_status = po_receipt_status.receipt_status
        FROM po_receipt_status
        WHERE po_receipt_status.id = po.id;
        """,
    )


@openupgrade.migrate()
def migrate(env, version):
    _compute_purchase_order_receipt_status(env)
