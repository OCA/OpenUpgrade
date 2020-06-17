# Copyright 2019 Eficent <http://www.eficent.com>
# Copyright 2019 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade

_column_renames = {
    'hr_holidays': [
        ('type', None),
        ('number_of_days', None),
    ],
    'hr_holidays_status': [
        ('double_validation', None),
        ('limit', None),
    ],
    'resource_calendar_leaves': [
        ('holiday_id', None),
    ]
 }

_field_renames = [
    ('hr.holidays', 'hr_holidays', 'number_of_days', 'number_of_days_display'),
    ('hr.holidays', 'hr_holidays', 'number_of_days_temp', 'number_of_days'),
]

_model_renames = [
    ('hr.holidays.status', 'hr.leave.type'),
]

_table_renames = [
    ('hr_holidays_status', 'hr_leave_type'),
]


@openupgrade.migrate()
def migrate(env, version):
    cr = env.cr
    openupgrade.rename_columns(cr, _column_renames)
    openupgrade.rename_fields(env, _field_renames)
    openupgrade.rename_models(cr, _model_renames)
    openupgrade.rename_tables(cr, _table_renames)
    openupgrade.logged_query(
        env.cr, "ALTER TABLE hr_leave_type ADD validity_start DATE"
    )
