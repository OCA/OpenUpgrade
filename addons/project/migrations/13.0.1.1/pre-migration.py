# Copyright 2020 Payam Yasaie <https://www.tashilgostar.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade

_xmlid_renames = [
    ('hr_timesheet.access_account_analytic_account_manager', 'project.access_account_analytic_account_manager'),
    ('hr_timesheet.access_account_analytic_account_user', 'project.access_account_analytic_account_user'),
    ('hr_timesheet.access_account_analytic_line_project', 'project.access_account_analytic_line_project'),
]


def fill_project_task_company_id(cr):
    openupgrade.logged_query(
        cr, """
        UPDATE project_task pt
        SET company_id = pp.company_id
        FROM project_project pp
        WHERE pp.id = pt.project_id AND pt.company_id IS NULL
        """
    )
    openupgrade.logged_query(
        cr, """
        UPDATE project_task pt
        SET company_id = ru.company_id
        FROM res_users ru
        WHERE pt.project_id IS NULL AND pt.company_id IS NULL AND pt.create_uid = ru.id
        """
    )


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.rename_xmlids(env.cr, _xmlid_renames)
    fill_project_task_company_id(env.cr)
    openupgrade.set_xml_ids_noupdate_value(
        env,
        "project",
        [
            "mt_project_task_blocked",
            "mt_project_task_new",
            "mt_project_task_rating",
            "mt_project_task_ready",
            "mt_project_task_stage",
            "mt_task_blocked",
            "mt_task_new",
            "mt_task_rating",
            "mt_task_ready",
            "mt_task_stage",
        ],
        True,
    )
