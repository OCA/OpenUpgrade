# Copyright 2025 Tecnativa - Carlos Lopez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade


def _delivery_carrier_map_delivery_type(env):
    delivery_type_legacy = openupgrade.get_legacy_name("delivery_type")
    openupgrade.map_values(
        env.cr,
        delivery_type_legacy,
        "delivery_type",
        [("onsite", "in_store")],
        table="delivery_carrier",
    )


def _payment_provider_map_custom_mode(env):
    custom_mode_legacy = openupgrade.get_legacy_name("custom_mode")
    openupgrade.map_values(
        env.cr,
        custom_mode_legacy,
        "custom_mode",
        [("onsite", "on_site")],
        table="payment_provider",
    )


def _handle_delivery_carrier_published(env):
    """
    Odoo now has a constraint on delivery carrier publication:
    the delivery carrier must be linked to a warehouse to be published.
    See: https://github.com/odoo/odoo/blob/08b2573f2ac2b812a0e7f8ebaf90db431124ac69/addons/website_sale_collect/models/delivery_carrier.py#L26
    Therefore, we need to unpublish delivery carriers that are not linked to a warehouse
    since in V17 the warehouse_id field was not required.
    """
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE delivery_carrier
        SET is_published = FALSE
        WHERE delivery_type = 'in_store'
        AND is_published = TRUE
        AND NOT EXISTS (
            SELECT 1
            FROM delivery_carrier_stock_warehouse_rel m2m
            WHERE m2m.delivery_carrier_id = delivery_carrier.id
        )
        """,
    )


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.m2o_to_x2m(
        env.cr,
        env["delivery.carrier"],
        "delivery_carrier",
        "warehouse_ids",
        "warehouse_id",
    )
    _delivery_carrier_map_delivery_type(env)
    _payment_provider_map_custom_mode(env)
    _handle_delivery_carrier_published(env)
    openupgrade.load_data(
        env, "website_sale_collect", "18.0.1.0/noupdate_changes_work.xml"
    )
    openupgrade.delete_record_translations(
        env.cr,
        "website_sale_collect",
        [
            "carrier_pick_up_in_store",
            "payment_provider_on_site",
            "product_pick_up_in_store",
        ],
    )
