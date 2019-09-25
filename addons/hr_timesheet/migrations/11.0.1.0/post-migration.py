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
    origin_issue_column = openupgrade.get_legacy_name('origin_issue_id')
    if not openupgrade.column_exists(env.cr, 'account_analytic_line',
                                     origin_issue_column):
        return
    openupgrade.logged_query(
        env.cr, """
        UPDATE account_analytic_line aal
        SET task_id = pt.id
        FROM project_task pt
        WHERE pt.%s = aal.issue_id""", (AsIs(origin_issue_column), ),
    )


def recompute_tasks_from_issues_fields(env):
    """This module adds several computed stored fields to project.task (for
    example, effective_hours and remaining_hours). Issues converted to tasks,
    being inserted by SQL, don't have these fields computed, so we force here
    its recomputation.
    """
    origin_issue_column = openupgrade.get_legacy_name('origin_issue_id')
    if not openupgrade.column_exists(env.cr, 'project_task',
                                     origin_issue_column):
        return
    env.cr.execute("SELECT id FROM project_task WHERE %s IS NOT NULL",
                   (AsIs(origin_issue_column), ))
    tasks = env['project.task'].browse([x[0] for x in env.cr.fetchall()])
    tasks._hours_get()


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.load_data(
        env.cr, 'hr_timesheet', 'migrations/11.0.1.0/noupdate_changes.xml',
    )
    update_employee_id(env)
    migrate_project_issue_sheet(env)
    recompute_tasks_from_issues_fields(env)
