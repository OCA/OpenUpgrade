# Copyright 2025 Tecnativa - Carlos Lopez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade

_columns_copy = {
    "delivery_carrier": [("delivery_type", None, None)],
    "payment_provider": [("custom_mode", None, None)],
}

# Use the module name website_sale_collect in old XML-IDs,
# because in the base it was renamed from website_sale_picking
_xmlids_renames = [
    (
        "website_sale_collect.default_onsite_carrier",
        "website_sale_collect.carrier_pick_up_in_store",
    ),
    (
        "website_sale_collect.payment_provider_onsite",
        "website_sale_collect.payment_provider_on_site",
    ),
    (
        "website_sale_collect.onsite_delivery_product",
        "website_sale_collect.product_pick_up_in_store",
    ),
    (
        "website_sale_collect.view_delivery_carrier_form_with_onsite_picking",
        "website_sale_collect.delivery_carrier_form",
    ),
    (
        "website_sale_collect.res_config_settings_view_form",
        "website_sale_collect.res_config_settings_form",
    ),
]


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.copy_columns(env.cr, _columns_copy)
    openupgrade.rename_xmlids(env.cr, _xmlids_renames)
