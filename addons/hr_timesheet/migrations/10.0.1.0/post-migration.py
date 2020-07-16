# -*- coding: utf-8 -*-
# Copyright 2017 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade


def migrate_allow_timesheets(env):
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE project_project pp
        SET allow_timesheets = True
        FROM account_analytic_account aaa
        WHERE aaa.id = pp.analytic_account_id
        AND aaa.%s = True
        """ % openupgrade.get_legacy_name('use_timesheets'),
    )


def migrate_missing_projects(env):
    """Create a project and link it to the orphaned analytic accounts"""
    env.cr.execute(
        """
        SELECT aaa.id, aaa.company_id, aaa.name, aaa.active, aaa.%(column)s
        FROM account_analytic_account aaa
        LEFT JOIN account_analytic_line aal ON aal.account_id = aaa.id
        LEFT JOIN project_project pp ON pp.analytic_account_id = aaa.id
        WHERE ((aal.is_timesheet AND aal.id IS NOT NULL) OR aaa.%(column)s)
            AND pp.id IS NULL
        GROUP BY aaa.id, aaa.company_id, aaa.name, aaa.active, aaa.%(column)s
        """ % {"column": openupgrade.get_legacy_name('use_timesheets')}
    )
    aaa_rows = env.cr.fetchall()
    project_obj = env['project.project']
    for aaa_row in aaa_rows:
        # It's easier to create the project via ORM
        project_obj.create({
            'analytic_account_id': aaa_row[0],
            'company_id': aaa_row[1],
            'name': aaa_row[2],
            'active': aaa_row[3],
            'allow_timesheets': aaa_row[4],
        })


def fill_analytic_line_project(env):
    """Fill project with the linked one in the related task, issue, or project
    related to the analytic account."""
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE account_analytic_line aal
        SET project_id = pt.project_id
        FROM project_task pt
        WHERE pt.id = aal.task_id
        AND pt.project_id IS NOT NULL
        AND aal.project_id IS NULL
        """,
    )
    if openupgrade.is_module_installed(env.cr, 'project_issue_sheet'):
        openupgrade.logged_query(
            env.cr,
            """
            UPDATE account_analytic_line aal
            SET project_id = pi.project_id
            FROM project_issue pi
            WHERE pi.id = aal.issue_id
            AND pi.project_id IS NOT NULL
            AND aal.project_id IS NULL
            """,
        )
    # Finally, try to link the rest of the lines that are not linked to a
    # task nor an issue to the project associated with the analytic account
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE account_analytic_line aal
        SET project_id = pp.id
        FROM project_project pp
        WHERE pp.analytic_account_id = aal.account_id
        AND aal.project_id IS NULL
        AND aal.is_timesheet IS True
        """,
    )


@openupgrade.migrate()
def migrate(env, version):
    migrate_allow_timesheets(env)
    migrate_missing_projects(env)
    fill_analytic_line_project(env)
