# Copyright 2020 Andrii Skrypka
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.map_values(
        env.cr,
        'measure_type',
        'measure_type',
        [('time', 'working_time')],
        table='uom_category',
    )
    openupgrade.load_data(env.cr, 'uom', 'migrations/13.0.1.0/noupdate_changes.xml')
