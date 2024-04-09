# Copyright 2024 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade

_fields_renames = [
    (
        "res.company",
        "res_company",
        "website_sale_onboarding_payment_acquirer_state",
        "website_sale_onboarding_payment_provider_state",
    ),
]
_xmlid_renames = [
    (
        "website_sale_stock_wishlist.ir_cron_send_availability_email",
        "website_sale.ir_cron_send_availability_email",
    )
]
_not_noupdate_xml_ids = [
    "s_dynamic_snippet_products_000_scss",
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
    "price_dynamic_filter_template_product_product",
]


def _remove_view_inheritance(env):
    """On v15, some views were inherited ones, but this it not anymore in v16. As Odoo
    only touches the fields that are present in the definition, and now the `inherit_id`
    field is missing, the inheritance keeps there, provoking a crash.

    Let's empty them manually by SQL (for avoiding view validation) and using the key,
    for any possible website specific view.
    """
    openupgrade.logged_query(
        env.cr,
        """UPDATE ir_ui_view SET inherit_id=NULL, mode='primary'
        WHERE key IN (
            'website_sale.sort',
            'website_sale.add_grid_or_list_option',
            'website_sale.products_categories',
            'website_sale.filter_products_price'
        )""",
    )


def _remove_incorrect_website_sale_extra_field_records(env):
    openupgrade.logged_query(
        env.cr,
        "DELETE FROM website_sale_extra_field WHERE field_id IS NULL",
    )


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.rename_fields(env, _fields_renames)
    openupgrade.rename_xmlids(env.cr, _xmlid_renames)
    openupgrade.set_xml_ids_noupdate_value(
        env, "website_sale", _not_noupdate_xml_ids, False
    )
    _remove_view_inheritance(env)
    _remove_incorrect_website_sale_extra_field_records(env)
