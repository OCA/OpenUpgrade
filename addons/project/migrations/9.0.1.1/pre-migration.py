# -*- coding: utf-8 -*-
# @ 2014-Today: Odoo Community Association, Microcom
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

xmlid_renames = [
    ('project.project_category_01', 'project.project_tags_00'),
    ('project.project_category_02', 'project.project_tags_01'),
    ('project.project_category_03', 'project.project_tags_02'),
    ('project.project_category_04', 'project.project_tags_03'),
]


@openupgrade.migrate()
def migrate(cr, version):
    openupgrade.copy_columns(cr, column_copies)
    openupgrade.rename_tables(cr, table_renames)
    openupgrade.rename_columns(cr, column_renames)
    openupgrade.rename_xmlids(cr, xmlid_renames)
