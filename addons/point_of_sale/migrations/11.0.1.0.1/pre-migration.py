# Copyright 2018 Tecnativa - Vicent Cubells
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.rename_columns(
        env.cr, {'pos_config': [('iface_tax_included', None)]})
    openupgrade.add_fields(env, [
        ('customer_facing_display_html', 'pos.config', 'pos_config', 'html',
         False, 'point_of_sale'),
    ])
