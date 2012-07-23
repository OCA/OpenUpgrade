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

import pooler, logging
from openupgrade import openupgrade

logger = logging.getLogger('OpenUpgrade: hr')

defaults = {
    # False results in column value NULL
    # None value triggers a call to the model's default function 
    #'account.fiscalyear': [
    #    ('company_id', None),
    #    ],    
    }

def create_employee_resources(cr, pool):
    employee_pool = pool.get('hr.employee')
    resource_pool = pool.get('resource.resource')
    cr.execute("""
SELECT 
    id,
    openupgrade_legacy_user_id,
    openupgrade_legacy_company_id,
    openupgrade_legacy_name,
    openupgrade_legacy_active
FROM hr_employee
WHERE resource_id is NULL
""")
    for row in cr.fetchall():
        resource_id = resource_pool.create(
            cr, 1, 
            {'user_id': row[1],
             'company_id': row[2],
             'name': row[3],
             'active': row[4],
             })
        employee_pool.write(
            cr, 1, row[0], {'resource_id': resource_id})
    
def get_user_employee(cr, pool, user_id):
    if not user_id:
        return False
    employee_pool = pool.get('hr.employee')
    employee_ids = employee_pool.search(
        cr, 1, [('user_id', '=', user_id)])
    if employee_ids:
        if len(employee_ids) > 1:
            logger.info(
                'user %d is associated with multiple active '
                'employees. Need to select one for department membership or '
                'manager' %  user_id)
        return employee_ids[0]
    return False

def set_department_manager(cr, pool):
    """
    Migrate department managment by user
    by management by employee.
    """
    department_pool = pool.get('hr.department')
    cr.execute( 'SELECT id, openupgrade_legacy_manager_user_id from hr_department')
    for row in cr.fetchall():
        employee_id = get_user_employee(
            cr, pool, row[1])
        if employee_id:
            department_pool.write(
                cr, 1, row[0], {'manager_id': employee_id})

def set_user_department(cr, pool):
    """
    Migrate department membership by user
    to membership by employee. 
    In OpenERP 6, an employee can only be in a single
    department.

    When the department is written on the employee record,
    the manager is taken to be the head of the department in 6.0.
    This change was reverted in 6.1. To accomodate migrations to 6.1,
    restore the original manager 
    """
    employee_pool = pool.get('hr.employee')
    cr.execute("""
SELECT
    user_id,
    department_id,
    hr_department.manager_id
FROM
    openupgrade_legacy_hr_department_user_rel,
    hr_department
WHERE
    openupgrade_legacy_hr_department_user_rel.department_id = hr_department.id
""")
    for row in cr.fetchall():
        employee_id = get_user_employee(cr, pool, row[0])
        if employee_id:
            if employee_id == row[2]:
                logger.info(
                    'OpenERP does not allow employee with id %s as a '
                    'member of the department that it is the manager of. '
                    % employee_id)
            else:
                employee_pool.write(
                    cr, 1, employee_id, {'department_id': row[1]})

    openupgrade.logged_query(cr, """
        UPDATE hr_employee
        SET parent_id = %s
    """ % openupgrade.get_legacy_name('parent_id'))

def set_marital(cr, pool):
    """
    Migrate selection field 'marital' to
    a many2one field of model hr.employee.marital.status
    """
    marital_pool = pool.get('hr.employee.marital.status')
    employee_pool = pool.get('hr.employee')
    def get_or_create(marital):
        marital = {
            'maried': 'Married',
            'unmaried': 'Single',
            'divorced': 'Divorced',
            'other': 'Other'
            }.get(marital, marital)
        ids = marital_pool.search(
            cr, 1, [('name', '=', marital)])
        if ids:
            return ids[0]
        return marital_pool.create(
            cr, 1, {'name': marital})
    # marital might already be filled by the renaming of
    # hr_contract's marital_status
    cr.execute('SELECT id, openupgrade_legacy_marital '
               'FROM hr_employee WHERE marital IS NULL '
               'AND openupgrade_legacy_marital IS NOT NULL')
    for row in cr.fetchall():
        employee_pool.write(
            cr, 1, row[0], {'marital': get_or_create(row[1])})

def set_department_manager(cr, pool):
    """
    Migrate department managment by user
    by management by employee.
    """
    department_pool = pool.get('hr.department')
    cr.execute( 'SELECT id, openupgrade_legacy_manager_user_id from hr_department')
    for row in cr.fetchall():
        employee_id = get_user_employee(
            cr, pool, row[1])
        if employee_id:
            department_pool.write(
                cr, 1, row[0], {'manager_id': employee_id})

def set_category_ids(cr, pool):
    """
    Migrate the many2one category_id field
    to many2many category_ids
    """
    employee_pool = pool.get('hr.employee')
    cr.execute('SELECT id, openupgrade_legacy_category_id '
               'FROM hr_employee '
               'WHERE openupgrade_legacy_category_id IS NOT NULL')
    for row in cr.fetchall():
        employee_pool.write(
            cr, 1, row[0], {'category_ids': [(4, row[1])]})

@openupgrade.migrate()
def migrate(cr, version):
    pool = pooler.get_pool(cr.dbname)
    openupgrade.set_defaults(cr, pool, defaults)
    create_employee_resources(cr, pool)
    set_department_manager(cr, pool)
    set_user_department(cr, pool)
    set_category_ids(cr, pool)
    # The following definitions were moved from hr_contract.
    # In case this module was installed, the reloading of the data
    # will only overwrite the name if it was altered
    openupgrade.load_xml(cr, 'hr', 'migrations/6.0.1.1/data.xml')
    set_marital(cr, pool)
