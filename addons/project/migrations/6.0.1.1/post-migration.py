# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    This migration script copyright (C) 2012 Therp BV (<http://therp.nl>)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

import pooler
from openupgrade import openupgrade

defaults = {
    'project.project': [('sequence', 10)],
    'project.task.type': [('sequence', 1)],
    }

defaults_force = {
    'project.task': [('company_id', None)],
    }

def migrate_analytic(cr, pool):
    """
    Transfer obsolete values from projects to their analytic accounts.
    Create analytic account if necessary. Take care not to overwrite 
    existing values on analytic accounts
    """
    project_pool = pool.get('project.project')
    analytic_pool = pool.get('account.analytic.account')
    project_ids = project_pool.search(
        cr, 1, 
        [('analytic_account_id', '!=', False)],
        context={'active_test': False})
    analytics = dict([(x.id, x.analytic_account_id) for x in project_pool.browse(
        cr, 1, project_ids)])
    cr.execute("""
        SELECT
            id,
            analytic_account_id,
            openupgrade_legacy_contact_id,
            openupgrade_legacy_date_start,
            openupgrade_legacy_date_end,
            openupgrade_legacy_manager,
            openupgrade_legacy_name,
            openupgrade_legacy_notes,
            openupgrade_legacy_partner_id,
            openupgrade_legacy_state
        FROM
            project_project
        """)
    for row in cr.fetchall():
        if not row[1]:
            analytic_id = analytic_pool.create(
                cr, 1, 
                { 'contact_id': row[2] or False,
                  'date_start': row[3] or False,
                  'date': row[4] or False,
                  'user_id' : row[5] or False,
                  'name': row[6] or False,
                  'description': row[7] or False,
                  'partner_id': row[8] or False,
                  'state': row[9] or False,
                  })
            project_pool.write(
                cr, 1, row[0],
                {'analytic_account_id': analytic_id})
        else:
            vals = {}
            for num, field in [
                (2, 'contact_id'),
                (3, 'date_start'),
                (4, 'date'),
                (5, 'user_id'),
                (6, 'name'),
                (7, 'description'),
                (8, 'partner_id'),
                (9, 'state')]:
                if row[num] and not analytics[row[0]][field]:
                    vals[field] = row[num]
            analytic_pool.write(
                cr, 1, row[1], vals)

    # second pass: transfer project hierarchy
    # to analytic hierarchy
    cr.execute("""
        SELECT
            child.analytic_account_id,
            parent.analytic_account_id
        FROM
            project_project as child,
            project_project as parent,
            account_analytic_account as a
        WHERE 
            child.openupgrade_legacy_parent_id = parent.id
            AND child.analytic_account_id = a.id
            AND a.parent_id IS NULL
        """)
    for row in cr.fetchall():
        analytic_pool.write(
            cr, 1, row[0],
            {'parent_id': row[1]})

def migrate_task_parent_ids(cr, pool):
    task_pool = pool.get('project.task')
    cr.execute("""
        SELECT
            id,
            openupgrade_legacy_parent_id
        FROM
            project_task
        WHERE
            openupgrade_legacy_parent_id IS NOT NULL
        """)
    for row in cr.fetchall():
        task_pool.write(
            cr, 1, row[0],
            {'parent_ids': [(4, row[1])]})

def migrate_company_time_mode(cr, pool):
    """
    Migrate a char selection to a many2one
    of model product.uom
    No standard resources available
    for less likely options 'week' and 'month'.
    Mention this in the user notes
    """
    data_pool = pool.get('ir.model.data')
    company_pool = pool.get('res.company')
    uom_map = {
        'day': data_pool.get_object_reference(
            cr, 1, 'product', 'uom_day')[1],
        'hours': data_pool.get_object_reference(
            cr, 1, 'product', 'uom_hour')[1],
        }
    cr.execute("""
        SELECT
            id,
            openupgrade_legacy_project_time_mode
        FROM
            res_company
        WHERE
            openupgrade_legacy_project_time_mode IS NOT NULL
        """)
    for row in cr.fetchall():
        if uom_map.get(row[1]):
            company_pool.write(
                cr, 1, row[0],
                {'project_time_mode_id': uom_map(row[1])})

@openupgrade.migrate()
def migrate(cr, version):
    pool = pooler.get_pool(cr.dbname)
    migrate_analytic(cr, pool)
    openupgrade.set_defaults(cr, pool, defaults)
    openupgrade.set_defaults(cr, pool, defaults_force, force=True)
    migrate_task_parent_ids(cr, pool)
