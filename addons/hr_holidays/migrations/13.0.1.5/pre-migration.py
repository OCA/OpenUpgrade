# Copyright 2020 Payam Yasaie <https://www.tashilgostar.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade

_column_copies = {
    'hr_leave': [
        ('request_hour_from', None, None),
        ('request_hour_to', None, None),
    ],
}

_column_renames = {
    'hr_leave_allocation': [
        ('accrual', None),
    ],
    'hr_leave_type': [
        ('categ_id', None),
    ],
}

_xmlid_renames = [
    # ir.actions.act_window.view
    ('hr_holidays.hhr_leave_action_new_request_view_form', 'hr_holidays.hr_leave_action_new_request_view_form'),
    # ir.rule
    ('hr_holidays.resource_leaves_officer', 'hr_holidays.resource_leaves_holidays_user'),
    # mail.message.subtype
    ('hr_holidays.mt_leave_allocation_approved', 'hr_holidays.mt_leave_allocation'),
    ('hr_holidays.mt_leave_approved', 'hr_holidays.mt_leave'),
]


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.copy_columns(env.cr, _column_copies)
    openupgrade.rename_columns(env.cr, _column_renames)
    openupgrade.rename_xmlids(env.cr, _xmlid_renames)
