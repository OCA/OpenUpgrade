# Copyright 2018 Tecnativa - Vicent Cubells
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade


def update_employee_id(env):
    openupgrade.logged_query(
        env.cr, """
            UPDATE account_analytic_line aal
            SET employee_id = (
              SELECT id
              FROM hr_employee
              WHERE user_id = aal.user_id
              LIMIT 1
            )
        """)


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.load_data(
        env.cr, 'hr_timesheet', 'migrations/11.0.1.0/noupdate_changes.xml',
    )
    update_employee_id(env)
