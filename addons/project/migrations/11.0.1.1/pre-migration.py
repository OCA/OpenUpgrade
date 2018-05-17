# -*- coding: utf-8 -*-
# Copyright 2017-2018 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade


renamed_xml_ids = [
    ('project.portal_project_rule', 'project.project_project_rule_portal'),
    ('project.portal_task_rule', 'project.project_task_rule_portal'),
]


def move_fields_from_module(env):
    openupgrade.update_module_moved_fields(
        env.cr, 'project.project', ['subtask_project_id'],
        'hr_timesheet', 'project',
    )
    openupgrade.update_module_moved_fields(
        env.cr, 'project.task', [
            'child_ids',
            'parent_id',
            'subtask_count',
            'subtask_project_id',
        ],
        'hr_timesheet', 'project',
    )


@openupgrade.migrate()
def migrate(env, version):
    move_fields_from_module(env)
    openupgrade.rename_xmlids(env.cr, renamed_xml_ids)
    openupgrade.delete_records_safely_by_xml_id(env, [
        'project.portal_issue_rule',  # Comes from website_project_issue
    ])
