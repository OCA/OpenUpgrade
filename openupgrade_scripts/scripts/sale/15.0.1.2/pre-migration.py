from openupgradelib import openupgrade

_columns_copy = {
    "sale_order": [
        ("note", None, None),
    ],
}


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.copy_columns(env.cr, _columns_copy)
    if openupgrade.column_exists(env.cr, "sale_order_line", "product_packaging"):
        openupgrade.rename_fields(
            env,
            [
                (
                    "sale.order.line",
                    "sale_order_line",
                    "product_packaging",
                    "product_packaging_id",
                )
            ],
        )
    openupgrade.add_fields(
        env,
        [
            (
                "sales",
                "product.packaging",
                "product_packaging",
                "boolean",
                "bool",
                "sale",
                True,
            )
        ],
    )
