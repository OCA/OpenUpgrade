# Copyright 2020 ForgeFlow <http://www.forgeflow.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade


def fill_delivery_carrier_invoice_policy(env):
    """Fill all delivery.carrier records to have `real` value in invoice_policy,
    as this is the most similar one to the v12 behavior.
    """
    openupgrade.logged_query(
        env.cr, "UPDATE delivery_carrier SET invoice_policy = 'real'"
    )


def fill_sale_order_recompute_delivery_price(env):
    openupgrade.logged_query(
        env.cr, """
        UPDATE sale_order
        SET recompute_delivery_price = TRUE
        WHERE carrier_id IS NOT NULL
        AND state IN ('draft', 'sent')"""
    )


@openupgrade.migrate()
def migrate(env, version):
    fill_delivery_carrier_invoice_policy(env)
    fill_sale_order_recompute_delivery_price(env)
    openupgrade.load_data(
        env.cr, "delivery", "migrations/13.0.1.0/noupdate_changes.xml")
