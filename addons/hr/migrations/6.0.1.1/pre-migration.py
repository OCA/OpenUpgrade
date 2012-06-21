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

from openupgrade import openupgrade

column_renames = {
    # this is a mapping per table from old column name
    # to new column name
    'hr_department': [
        ('manager_id', 'openupgrade_legacy_manager_user_id'),
        ],
    'hr_employee': [
        ('user_id', 'openupgrade_legacy_user_id'),
        ('name', 'openupgrade_legacy_name'),
        ('active', 'openupgrade_legacy_active'),
        ('company_id', 'openupgrade_legacy_company_id'),
        ('category_id', 'openupgrade_legacy_category_id'),
        ('marital', 'openupgrade_legacy_marital'),
        ('parent_id', 'openupgrade_legacy_parent_id'),
        ]
    }

renamed_xmlids = [
    ('hr.group_hr_user', 'base.group_hr_user'),
    ('hr.group_hr_manager', 'base.group_hr_manager'),
    ('hr_contract.hr_employee_marital_status_divorced',
     'hr.hr_employee_marital_status_divorced'),
    ('hr_contract.hr_employee_marital_status_married',
     'hr.hr_employee_marital_status_married'),
    ('hr_contract.hr_employee_marital_status_single',
     'hr.hr_employee_marital_status_single'),
    ('hr_contract.hr_employee_marital_status_widower',
     'hr.hr_employee_marital_status_widower'),
]     
   
@openupgrade.migrate()
def migrate(cr, version):
    openupgrade.rename_columns(cr, column_renames)
    # marital status as provided by hr_contract if installed
    if openupgrade.column_exists(
        cr, 'hr_employee', 'marital_status'):
        openupgrade.rename_columns(
            cr, { 'hr_employee': [('marital_status', 'marital')]})
    openupgrade.rename_tables(
        cr, 
        [('hr_department_user_rel',
          'openupgrade_legacy_hr_department_user_rel')])
    openupgrade.rename_xmlids(cr, renamed_xmlids)

