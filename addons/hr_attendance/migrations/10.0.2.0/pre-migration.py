# -*- coding: utf-8 -*-
# Copyright 2017 Tecnativa - Vicent Cubells
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade

_column_renames = {
    'hr_attendance': [
        ('action', None),
        ('name', 'check_in'),
    ],
}


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.rename_columns(env.cr, _column_renames)
    env.ref('hr_attendance.property_rule_attendace_manager').unlink()
    env.ref('hr_attendance.property_rule_attendace_employee').unlink()
