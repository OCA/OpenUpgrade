# Copyright 2021 ForgeFlow S.L.  <https://www.forgeflow.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade

_xmlid_renames = [
    (
        "sale.access_product_product_attribute_custom_value",
        "sale.access_product_product_attribute_custom_value_sale_manager",
    ),
    ("sale.account_move_see_all", "sale.account_invoice_rule_see_all"),
    ("sale.account_move_personal_rule", "sale.account_invoice_rule_see_personal"),
    ("sale.account_move_line_see_all", "sale.account_invoice_line_rule_see_all"),
    (
        "sale.account_move_line_personal_rule",
        "sale.account_invoice_line_rule_see_personal",
    ),
]


def fast_fill_sale_order_currency_id(env):
    if not openupgrade.column_exists(env.cr, "sale_order", "currency_id"):
        openupgrade.logged_query(
            env.cr,
            """
            ALTER TABLE sale_order
            ADD COLUMN currency_id integer""",
        )
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE sale_order so
        SET currency_id = pp.currency_id
        FROM product_pricelist pp
        WHERE so.pricelist_id = pp.id""",
    )


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.rename_xmlids(env.cr, _xmlid_renames)
    fast_fill_sale_order_currency_id(env)
