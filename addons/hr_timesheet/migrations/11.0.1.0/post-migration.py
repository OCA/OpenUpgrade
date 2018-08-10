# Copyright 2018 Tecnativa - Vicent Cubells
# Copyright 2018 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade
from psycopg2.extensions import AsIs


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


def migrate_project_issue_sheet(env):
    """Detect through column existence if project_issue_sheet was installed
    and then fill `task_id` field in analytic lines with the tasks created
    from issues.
    """
    if not openupgrade.column_exists(
            env.cr, 'account_analytic_line', 'issue_id'):
        return
    origin_issue_column = openupgrade.get_legacy_name('origin_issue_id')
    openupgrade.logged_query(
        env.cr, """
        UPDATE account_analytic_line aal
        SET task_id = pt.id
        FROM project_task pt
        WHERE pt.%s = aal.issue_id""", (AsIs(origin_issue_column), ),
    )


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.load_data(
        env.cr, 'hr_timesheet', 'migrations/11.0.1.0/noupdate_changes.xml',
    )
    update_employee_id(env)
    migrate_project_issue_sheet(env)
