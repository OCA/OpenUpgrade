# Copyright 2020 Andrii Skrypka
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade

_column_copies = {
    'uom_category': [
        ('measure_type', None, None),
    ],
}


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.copy_columns(env.cr, _column_copies)
    openupgrade.map_values(
        env.cr,
        openupgrade.get_legacy_name('measure_type'),
        'measure_type',
        [('time', 'working_time')],
        table='uom_category',
    )
