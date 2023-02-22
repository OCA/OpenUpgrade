from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.convert_field_to_html(
        env.cr, "product_template", "custom_message", "custom_message"
    )
    openupgrade.rename_fields(
        env,
        [
            (
                "product.template",
                "product_template",
                "custom_message",
                "out_of_stock_message",
            ),
        ],
    )
