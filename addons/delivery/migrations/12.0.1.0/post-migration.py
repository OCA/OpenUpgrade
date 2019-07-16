# Copyright 2019 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.load_data(
        env.cr, 'delivery', 'migrations/12.0.1.0/noupdate_changes.xml')
    openupgrade.delete_record_translations(
        env.cr,
        'delivery',
        ['mail_template_data_delivery_confirmation'],
    )
