# -*- coding: utf-8 -*-
# Copyright 2017 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade

COLUMN_RENAMES = {
    'account_analytic_account': [
        ('use_timesheets', None),
    ]
}


def create_and_populate_department(cr):
    cr.execute('''
       ALTER TABLE account_analytic_line ADD COLUMN department_id INT;

       WITH departments AS (
          SELECT r.user_id AS user_id, MAX(e.department_id) AS dpt_id
             FROM hr_employee e JOIN resource_resource r
                                ON e.resource_id = r.id
          GROUP BY user_id
       )
       UPDATE account_analytic_line aal SET department_id=departments.dpt_id
       FROM departments WHERE aal.user_id = departments.user_id;
    ''')


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.rename_columns(env.cr, COLUMN_RENAMES)
    create_and_populate_department(env.cr)
