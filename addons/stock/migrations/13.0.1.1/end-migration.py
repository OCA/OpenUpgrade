# Copyright 2022 ForgeFlow <https://www.forgeflow.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    # xmlids are deprecated in v13
    openupgrade.logged_query(env.cr, """
    DELETE FROM ir_model_data imd
    WHERE imd.module = 'stock' AND imd.name IN (
        'property_stock_inventory', 'property_stock_production',
        'stock_location_scrapped', 'location_inventory', 'location_production',
        'location_procurement')
    """)
