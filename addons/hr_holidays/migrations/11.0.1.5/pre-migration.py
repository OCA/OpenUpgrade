# Copyright 2018 Tecnativa - Vicent Cubells
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade

field_renames = [
    ('hr.holidays', 'hr_holidays', 'manager_id2', 'second_approver_id')
]


@openupgrade.migrate(use_env=True)
def migrate(env, version):
    openupgrade.rename_fields(env, field_renames)
    openupgrade.add_fields(
        env, [
            ('first_approver_id', 'hr.holidays', 'hr_holidays', 'many2one',
             False, 'hr_holidays'),
        ],
    )
    openupgrade.logged_query(
        env.cr, "UPDATE hr_holidays SET first_approver_id = manager_id"
    )
