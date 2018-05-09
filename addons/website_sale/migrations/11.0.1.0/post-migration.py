# Copyright 2018 Tecnativa - Vicent Cubells
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.map_values(
        env.cr, openupgrade.get_legacy_name('type'),
        'type', [('hidden', 'select')], table='product_attribute',
    )
    openupgrade.load_data(
        env.cr, 'website_sale', 'migrations/11.0.1.0/noupdate_changes.xml',
    )
