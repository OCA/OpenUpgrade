from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    all_purchase_order_lines = env["purchase.order.line"].search(
        [
            ("product_packaging_id", "!=", False),
            ("state", "in", ["draft", "sent", "to approve"]),
        ]
    )
    for line in all_purchase_order_lines:
        line._onchange_suggest_packaging()
        line._onchange_update_product_packaging_qty()
