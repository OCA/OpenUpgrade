# -*- coding: utf-8 -*-
# Copyright 2017 Tecnativa - Vicent Cubells
# Copyright 2017 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade

_field_renames = [
    ('hr.attendance', 'hr_attendance', 'name', 'check_in'),
]


@openupgrade.migrate()
def migrate(env, version):
    # As there are indexes, foreign keys, and so on, we need to keep the
    # original table, copy it and remove records, instead of renaming and copy
    # only sign in records
    openupgrade.logged_query(
        env.cr,
        """CREATE TABLE %s AS (
            SELECT * FROM hr_attendance
        )""" % openupgrade.get_legacy_name('hr_attendance')
    )
    openupgrade.logged_query(
        env.cr,
        """DELETE FROM hr_attendance
        WHERE action != 'sign_in'"""
    )
    openupgrade.rename_fields(env, _field_renames)
    env.ref('hr_attendance.property_rule_attendace_manager').unlink()
    env.ref('hr_attendance.property_rule_attendace_employee').unlink()
