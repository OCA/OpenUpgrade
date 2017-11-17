# -*- coding: utf-8 -*-
# Copyright 2017 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade


def cleanup_translations(cr):
    """
    Cleanup translations of adopted templates
    """

    updated_templates = (
        'mail_template_data_module_install_project',
    )

    openupgrade.delete_record_translations(cr, 'project', updated_templates)


def convert_issues(env):
    """
    As project_issue was removed, the recommendation was to use the existing
    issues in a new project as tasks.
    - For projects with issues, a new project is created with
    the same name plus ' Issues'. Some of the information of the main
    project is transferred to the new created one.
    - For every issue, a new task is created in the new project, transfering
    as much information from the issue as possible.
    :param env:
    :return:
    """

    projects = env['project.project'].search([])

    for project in projects:
        if len(project.issue_ids) > 0:
            new_name = project.name + ' (Issues)'
            new_project = env['project.project'].create({
                'name': new_name,
                'active': project.active,
                'favorite_user_ids': [(6, 0, project.favorite_user_ids.ids)],
                'label_tasks': project.label_issues,
                'type_ids': [(6, 0, project.type_ids.ids)],
                'color': project.color,
                'user_id': project.user_id.id,
                'alias_id': project.alias_id.id,
                'alias_model': project.alias_model,
                'privacy_visibility': project.privacy_visibility,
                'date_start': project.date_start,
                'date': project.date,
            })
            for issue in project.issue_ids:
                env['project.task'].create({
                    'project_id': new_project.id,
                    'active': issue.active,
                    'color': issue.color,
                    'company_id': issue.company_id.id,
                    'date_start': issue.date_open,
                    'date_end': issue.date_closed,
                    'date_deadline': issue.date_deadline,
                    'description': issue.description,
                    'kanban_state': issue.kanban_state,
                    'name': issue.name,
                    'partner_id': issue.partner_id.id,
                    'stage_id': issue.stage_id.id,
                    'tag_ids': [(6, 0, issue.tag_ids.ids)],
                    'user_id': issue.user_id.id
                })


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.load_data(
        env.cr, 'project', 'migrations/11.0.1.1/noupdate_changes.xml'
    )
    cleanup_translations(env.cr)
    convert_issues(env)
