# Copyright 2023 Tecnativa - Pilar Vargas

import random

from openupgradelib import openupgrade

_xmlids_renames = [
    (
        "sale_loyalty.sale_coupon_apply_code_action",
        "sale_loyalty.sale_loyalty_coupon_wizard_action",
    ),
    (
        "sale_loyalty.menu_coupon_type_config",
        "sale_loyalty.menu_discount_loyalty_type_config",
    ),
    (
        "sale_loyalty.menu_promotion_type_config",
        "sale_loyalty.menu_gift_ewallet_type_config",
    ),
    (
        "sale_loyalty.sale_coupon_view_form",
        "sale_loyalty.loyalty_card_view_form_inherit_sale_loyalty",
    ),
    (
        "sale_loyalty.sale_coupon_apply_code_view_form",
        "sale_loyalty.sale_loyalty_coupon_wizard_view_form",
    ),
    (
        "sale_loyalty.sale_order_view_form",
        "sale_loyalty.sale_order_view_form_inherit_sale_loyalty",
    ),
]


def _generate_random_reward_code():
    """This function, _generate_random_reward_code, provides a random reward code. It is
    used to create unique codes that identify rewards within the sale_loyalty module."""
    return str(random.getrandbits(32))


def update_loyalty_program_data(env):
    # Set sale_ok default values
    if not openupgrade.column_exists(env.cr, "loyalty_program", "sale_ok"):
        openupgrade.add_fields(
            env,
            [
                (
                    "sale_ok",
                    "loyalty.program",
                    "loyalty_program",
                    "boolean",
                    "bool",
                    "sale_loyalty",
                    True,
                )
            ],
        )


def update_sale_order_line_data(env):
    # Fill reward_id field
    openupgrade.logged_query(
        env.cr,
        """
        ALTER TABLE sale_order_line
        ADD COLUMN IF NOT EXISTS reward_id INT
        """,
    )
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE sale_order_line sol
        SET reward_id = lr.id
        FROM loyalty_reward lr
        WHERE sol.product_id = lr.discount_line_product_id
        """,
    )
    # Fill coupon_id field(env):
    openupgrade.logged_query(
        env.cr,
        """
        ALTER TABLE sale_order_line
        ADD COLUMN IF NOT EXISTS coupon_id INT
        """,
    )
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE sale_order_line
        SET coupon_id = loyalty_card.id
        FROM loyalty_card
        WHERE sale_order_line.order_id = loyalty_card.sales_order_id
        """,
    )
    # Fill reward_identifier_code
    openupgrade.logged_query(
        env.cr,
        """
        ALTER TABLE sale_order_line
        ADD COLUMN IF NOT EXISTS reward_identifier_code VARCHAR
        """,
    )
    env.cr.execute(
        """
        SELECT id
        FROM sale_order_line
        WHERE reward_id IS NOT NULL
        """
    )
    order_lines = env.cr.fetchall()
    # Update each order line with a unique reward code
    for line in order_lines:
        reward_code = _generate_random_reward_code()
        env.cr.execute(
            """
            UPDATE sale_order_line
            SET reward_identifier_code = %s
            WHERE id = %s
            """,
            (reward_code, line[0]),
        )
    # Fill points_cost field
    openupgrade.logged_query(
        env.cr,
        """
        ALTER TABLE sale_order_line
        ADD COLUMN IF NOT EXISTS points_cost FLOAT
        """,
    )
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE sale_order_line
        SET points_cost = ABS(untaxed_amount_to_invoice)
        WHERE reward_id IS NOT NULL
        AND untaxed_amount_to_invoice < 0
        """,
    )


def update_template_keys(env):
    """Update template keys of the merged sale_gift_card module in loyalty_sale"""
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE ir_ui_view
        SET key = 'sale_loyalty.used_gift_card'
        WHERE key = 'sale_gift_card.used_gift_card'
        """,
    )
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE ir_ui_view
        SET key = 'sale_loyalty.sale_purchased_gift_card'
        WHERE key = 'sale_gift_card.sale_purchased_gift_card'
        """,
    )
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE ir_ui_view
        SET key = 'sale_loyalty.sale_order_portal_content_inherit'
        WHERE key = 'sale_gift_card.sale_order_portal_content_inherit'
        """,
    )


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.rename_xmlids(env.cr, _xmlids_renames)
    update_loyalty_program_data(env)
    update_sale_order_line_data(env)
    update_template_keys(env)
