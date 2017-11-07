# -*- coding: utf-8 -*-
# Copyright 2014 Microcom
# Copyright 2017 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade

column_renames = {
    'project_issue': [
        ('version_id', None),
    ],
    'project_issue_project_tags_rel': [
        ('project_category_id', 'project_tags_id'),
    ],
}

field_renames = [
    # renamings with oldname attribute - They also need the rest of operations
    ('project.issue', 'project_issue', 'section_id', 'team_id'),
]

table_renames = [
    (
        'project_category_project_issue_rel',
        'project_issue_project_tags_rel',
    ),
]

xmlid_renames = [
    (
        'project_issue.project_issue_category_01',
        'project_issue.project_issue_tags_00'
    ),
    (
        'project_issue.project_issue_category_02',
        'project_issue.project_issue_tags_01'
    ),
    (
        'project_issue.project_issue_category_03',
        'project_issue.project_issue_tags_02'
    ),
]


@openupgrade.migrate(use_env=True)
def migrate(env, version):
    cr = env.cr
    openupgrade.rename_xmlids(cr, xmlid_renames)
    openupgrade.rename_tables(cr, table_renames)
    openupgrade.rename_columns(cr, column_renames)
    openupgrade.rename_fields(env, field_renames)
