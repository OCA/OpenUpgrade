# -*- coding: utf-8 -*-
# © 2015 Eficent Business and IT Consulting Services S.L. -
# Jordi Ballester Alomar
# © 2015 Serpent Consulting Services Pvt. Ltd. - Sudhir Arya
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade


column_copies = {
    'project_task': [
        ('description', None, None),
        ('priority', None, None),
    ],
    'project_project': [
        ('state', None, None),
    ],
}

# These column is kept even though it is removed in v9, in order to allow recovery by a future OCA module.
column_renames = {
    'project_task': [
        ('reviewer_id', None),
    ],
    # rename table and key
    'project_tags_project_task_rel': [
        ('project_category_id', 'project_tags_id'),
    ],
}

table_renames = [
    ('project_category', 'project_tags'),
    ('project_category_project_task_rel', 'project_tags_project_task_rel'),
    ]


column_drops = [
    ('project_config_settings', 'module_sale_service'),
    ('project_config_settings', 'module_pad'),
    ('project_config_settings', 'module_project_issue_sheet'),
    ('project_config_settings', 'group_time_work_estimation_tasks'),
    ('project_config_settings', 'module_project_timesheet'),
    ]


@openupgrade.migrate()
def migrate(cr, version):
    openupgrade.copy_columns(cr, column_copies)
    openupgrade.rename_tables(cr, table_renames)
    openupgrade.rename_columns(cr, column_renames)
    if openupgrade.column_exists(cr, 'project_project', 'members'):
        openupgrade.rename_columns(cr, {'project_project': [('members', None)]})
    # Removing transient tables to get rid of warnings
    openupgrade.drop_columns(cr, column_drops)
