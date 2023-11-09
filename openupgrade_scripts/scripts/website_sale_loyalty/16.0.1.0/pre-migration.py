# Copyright 2023 Tecnativa - Pilar Vargas
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade

_xmlids_renames = [
    (
        "website_sale_loyalty.coupon_view_tree",
        "website_sale_loyalty.loyalty_card_view_tree_inherit_website_sale_loyalty",
    ),
    (
        "website_sale_loyalty.res_config_settings_view_form",
        "website_sale_loyalty.res_config_settings_view_form_inherit_website_sale_loyalty",
    ),
    (
        "website_sale_loyalty.menu_promotion_type_config",
        "website_sale_loyalty.menu_discount_loyalty_type_config",
    ),
    (
        "website_sale_loyalty.menu_coupon_type_config",
        "website_sale_loyalty.menu_gift_ewallet_type_config",
    ),
]
_key_updates = [
    ("website_sale_coupon.cart_discount", "website_sale_loyalty.cart_discount"),
    ("website_sale_coupon.cart_summary", "website_sale_loyalty.cart_summary"),
    ("website_sale_coupon.layout", "website_sale_loyalty.layout"),
    ("website_sale_coupon.sale_coupon_result", "website_sale_loyalty.modify_code_form"),
    (
        "website_sale_coupon.website_sale_coupon_cart_hide_qty",
        "website_sale_loyalty.website_sale_coupon_cart_hide_qty",
    ),
    (
        "website_sale_coupon.reduction_coupon_code",
        "website_sale_loyalty.reduction_coupon_code",
    ),
    (
        "website_sale_gift_card.cart_line_product_no_link",
        "website_sale_loyalty.cart_line_product_no_link",
    ),
    (
        "website_sale_gift_card.cart_summary_inherit_website_gift_card_sale",
        "website_sale_loyalty.cart_summary_inherit_website_gift_card_sale",
    ),
    (
        "website_sale_gift_card.website_sale_purchased_gift_card",
        "website_sale_loyalty.website_sale_purchased_gift_card",
    ),
]


def update_loyalty_program_data(env):
    openupgrade.logged_query(
        env.cr,
        """
        ALTER TABLE loyalty_program
        ADD COLUMN IF NOT EXISTS ecommerce_ok BOOLEAN
        """,
    )
    # By default ecommerce_ok is true
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE loyalty_program
        SET ecommerce_ok = true
        """,
    )


def update_loyalty_rule_data(env):
    openupgrade.logged_query(
        env.cr,
        """
        ALTER TABLE loyalty_rule
        ADD COLUMN IF NOT EXISTS website_id INT
        """,
    )
    # Default is NULL (all websites) except for records coming from the merger of
    # website_sale_gift_card into website_sale_loyalty which may have a website defined.
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE loyalty_rule AS lr
        SET website_id = gc.website_id
        FROM gift_card AS gc
        WHERE lr.program_id = gc.program_id
        """,
    )


def update_template_keys(env, _key_updates):
    for old_key, new_key in _key_updates:
        openupgrade.logged_query(
            env.cr,
            "UPDATE ir_ui_view SET key = %s WHERE key = %s",
            (new_key, old_key),
        )


@openupgrade.migrate()
def migrate(env, version):
    update_loyalty_program_data(env)
    update_template_keys(env, _key_updates)
    openupgrade.rename_xmlids(env.cr, _xmlids_renames)
