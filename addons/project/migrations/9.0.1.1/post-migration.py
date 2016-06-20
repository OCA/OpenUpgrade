# -*- coding: utf-8 -*-
# © 2015 Eficent Business and IT Consulting Services S.L. -
# Jordi Ballester Alomar
# © 2015 Serpent Consulting Services Pvt. Ltd. - Sudhir Arya
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

import logging
from openupgradelib import openupgrade
logger = logging.getLogger('OpenUpgrade')

# copied from pre-migration
column_copies = {
    'project_task': [
        ('description', None, None),
    ],
}

def drop_null(cr):
    openupgrade.logged_query(cr, """
        ALTER TABLE account_analytic_line
        ALTER COLUMN amount DROP NOT NULL
        """)

def create_task_id(cr):
    openupgrade.logged_query(cr, """
        ALTER TABLE account_analytic_line
        ADD task_id integer
        """)

def assign_task_work(cr):
    openupgrade.logged_query(cr, """
        INSERT INTO account_analytic_line
        (name, date, unit_amount, user_id, task_id, amount, account_id)
        SELECT name, date, hours, user_id, task_id, '0.0',
        (SELECT p.analytic_account_id from project_project p join
        project_task t on p.id = t.project_id where t.id = task_id)
        FROM project_task_work
        """)

def map_priority(cr):
    openupgrade.map_values(
        cr,
        openupgrade.get_legacy_name('priority'),
        'priority',
        [('2', '1')],
        table='project_task', write='sql')

def map_template_state(cr):
    openupgrade.map_values(
        cr,
        openupgrade.get_legacy_name('state'),
        'state',
        [('template', 'draft')],
        table='project_project', write='sql')

def copy_user_id(cr):
    openupgrade.logged_query(cr, """
        UPDATE project_project p
        SET user_id = a.user_id
        FROM account_analytic_account a
        WHERE a.id = p.analytic_account_id
        """)

@openupgrade.migrate()
def migrate(cr, version):
    #drop_null(cr)
    map_priority(cr)
    map_template_state(cr)
    create_task_id(cr)
    assign_task_work(cr)
    copy_user_id(cr)
    for table_name in column_copies.keys():
        for (old, new, field_type) in column_copies[table_name]:
            openupgrade.convert_field_to_html(cr, table_name, openupgrade.get_legacy_name(old), old)
