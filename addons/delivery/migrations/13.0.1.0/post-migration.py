# Copyright 2020 ForgeFlow <http://www.forgeflow.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade


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
    fill_sale_order_recompute_delivery_price(env)
    openupgrade.load_data(
        env.cr, "delivery", "migrations/13.0.1.0/noupdate_changes.xml")
