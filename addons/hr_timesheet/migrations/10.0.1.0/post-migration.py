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
        SELECT aaa.id, aaa.company_id, aaa.name
        FROM account_analytic_account aaa
        LEFT JOIN project_project pp ON pp.analytic_account_id = aaa.id
        WHERE %s = True
        AND pp.id IS NULL
        """ %
        openupgrade.get_legacy_name('use_timesheets')
    )
    aaa_rows = env.cr.fetchall()
    project_obj = env['project.project']
    for aaa_row in aaa_rows:
        # It's easier to create the project via ORM
        project_obj.create({
            'analytic_account_id': aaa_row[0],
            'company_id': aaa_row[1],
            'name': aaa_row[2],
            'allow_timesheets': True,
        })


def fill_analytic_line_project(env):
    """Fill project with the linked one in the related task or issue."""
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


@openupgrade.migrate()
def migrate(env, version):
    migrate_allow_timesheets(env)
    migrate_missing_projects(env)
    fill_analytic_line_project(env)
