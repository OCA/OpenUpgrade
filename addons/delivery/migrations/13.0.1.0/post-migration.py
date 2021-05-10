# Copyright 2020 ForgeFlow <http://www.forgeflow.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade


def update_delivery_carrier_invoice_policy(env):
    """Update delivery.carrier records to have `real` value in invoice_policy
    only if all its sale orders have invoice_shipping_on_delivery = True.
    """
    openupgrade.logged_query(
        env.cr, """
        WITH carriers_to_real AS (
            SELECT dc.id
            FROM sale_order so
            JOIN delivery_carrier dc ON so.carrier_id = dc.id
            GROUP by dc.id
            HAVING bool_and(so.invoice_shipping_on_delivery)
        )
        UPDATE delivery_carrier dc
        SET invoice_policy = 'real'
        FROM carriers_to_real
        WHERE carriers_to_real.id = dc.id"""
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
    update_delivery_carrier_invoice_policy(env)
    fill_sale_order_recompute_delivery_price(env)
    openupgrade.load_data(
        env.cr, "delivery", "migrations/13.0.1.0/noupdate_changes.xml")
