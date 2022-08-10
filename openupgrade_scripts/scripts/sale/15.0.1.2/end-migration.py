from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    all_sale_order_lines = env["sale.order.line"].search(
        [("product_packaging_id", "!=", False), ("state", "in", ["draft", "sent"])]
    )
    for line in all_sale_order_lines:
        line._onchange_suggest_packaging()
        line._onchange_update_product_packaging_qty()
