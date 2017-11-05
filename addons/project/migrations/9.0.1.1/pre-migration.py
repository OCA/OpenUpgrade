# -*- coding: utf-8 -*-
# Copyright 2014-Today: Odoo Community Association, Microcom
# Copyright 2015 Eficent Business and IT Consulting Services S.L. -
# Jordi Ballester Alomar
# Copyright 2015 Serpent Consulting Services Pvt. Ltd. - Sudhir Arya
# Copyright 2017 Tecnativa - Pedro M. Baeza
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

field_renames = [
    # renamings with oldname attribute - They also need the rest of operations
    ('project.task', 'project_task', 'categ_ids', 'tag_ids'),
]

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


def recreate_analytic_lines(cr):
    """If the module project_timesheet is not installed, we need to convert
    project.task.work elements, or we will lose this history.

    This is done inserting new records in account_analytic_line, and adding one
    extra column work_id in case other modules need to fill some fields for
    each created line.
    """
    cr.execute("ALTER TABLE account_analytic_line ADD task_id integer")
    cr.execute("ALTER TABLE account_analytic_line ADD work_id integer")
    if not openupgrade.column_exists(cr, 'account_analytic_line',
                                     'is_timesheet'):
        cr.execute(
            "ALTER TABLE account_analytic_line ADD is_timesheet boolean")
    # TODO: Calculate line cost according employee data
    openupgrade.logged_query(
        cr,
        """
        INSERT INTO account_analytic_line
        (company_id, date, name, task_id, user_id, unit_amount, account_id,
         amount, is_timesheet, work_id)
        SELECT
            w.company_id, COALESCE(w.date, w.create_date),
            COALESCE(w.name, '(migrated line)'), w.task_id, w.user_id,
            w.hours, p.analytic_account_id, 0, True, w.id
        FROM
            project_task_work w,
            project_task t,
            project_project p
        WHERE
            w.task_id = t.id AND
            t.project_id = p.id
        """
    )


@openupgrade.migrate(use_env=True)
def migrate(env, version):
    cr = env.cr
    openupgrade.copy_columns(cr, column_copies)
    openupgrade.rename_tables(cr, table_renames)
    openupgrade.rename_columns(cr, column_renames)
    openupgrade.rename_fields(env, field_renames)
    openupgrade.rename_xmlids(cr, xmlid_renames)
    if not openupgrade.is_module_installed(cr, 'project_timesheet'):
        recreate_analytic_lines(cr)
    cr.execute(
        '''update ir_module_module set state='to install'
        where name='project_timesheet' and
        state in ('uninstalled', 'to remove') and
        exists (select id from ir_module_module where name='hr_timesheet'
        and state in ('to upgrade', 'to_install', 'installed'))''')
