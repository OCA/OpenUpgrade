# Copyright 2018 Tecnativa - Vicent Cubells
# Copyright 2018 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade


def update_employee_id(env):
    openupgrade.logged_query(
        env.cr, """
        UPDATE account_analytic_line aal
        SET employee_id = emp.id
        FROM hr_employee emp,
            resource_resource res
        WHERE aal.user_id = res.user_id
            AND emp.resource_id = res.id""",
    )


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.load_data(
        env.cr, 'hr_timesheet', 'migrations/11.0.1.0/noupdate_changes.xml',
    )
    update_employee_id(env)
