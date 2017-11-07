# -*- coding: utf-8 -*-
# Copyright 2017 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade


def assign_check_out(env):
    """Move name value to check_out column in matching 'sign_in' record for
    records where action='sign_out'.
    """
    openupgrade.logged_query(
        env.cr,
        """UPDATE hr_attendance a
        SET check_out = (
            SELECT name
            FROM %s
            WHERE action = 'sign_out'
            AND name > a.check_in
            AND employee_id = a.employee_id
            ORDER BY name
            LIMIT 1
        )
        """ % openupgrade.get_legacy_name('hr_attendance')
    )
    # Recompute worked hours
    env['hr.attendance'].search([])._compute_worked_hours()


@openupgrade.migrate()
def migrate(env, version):
    assign_check_out(env)
