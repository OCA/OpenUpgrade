from openupgradelib import openupgrade


def _fill_add_to_cart_action_value(env):
    openupgrade.logged_query(
        env.cr,
        """
        ALTER TABLE website
        ADD COLUMN IF NOT EXISTS add_to_cart_action VARCHAR
        """,
    )
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE website
        SET add_to_cart_action = CASE
            WHEN cart_add_on_page = TRUE THEN 'stay'
            ELSE 'go_to_cart'
        END
        """,
    )


@openupgrade.migrate()
def migrate(env, version):
    _fill_add_to_cart_action_value(env)
    openupgrade.rename_fields(
        env,
        [
            (
                "res.company",
                "res_company",
                "website_sale_onboarding_payment_acquirer_state",
                "website_sale_onboarding_payment_provider_state",
            ),
        ],
    )
    openupgrade.rename_xmlids(
        env.cr,
        [
            (
                "website_sale_stock_wishlist.ir_cron_send_availability_email",
                "website_sale.ir_cron_send_availability_email",
            ),
        ],
    )
    openupgrade.set_xml_ids_noupdate_value(
        env,
        "website_sale",
        [
            "s_dynamic_snippet_products_000_scss",
            "price_dynamic_filter_template_product_product",
            "dynamic_filter_template_product_product_add_to_cart",
            "dynamic_filter_template_product_product_banner",
            "dynamic_filter_template_product_product_borderless_1",
            "dynamic_filter_template_product_product_borderless_2",
            "dynamic_filter_template_product_product_centered",
            "dynamic_filter_template_product_product_horizontal_card",
            "dynamic_filter_template_product_product_mini_image",
            "dynamic_filter_template_product_product_mini_name",
            "dynamic_filter_template_product_product_mini_price",
            "dynamic_filter_template_product_product_view_detail",
        ],
        False,
    )
