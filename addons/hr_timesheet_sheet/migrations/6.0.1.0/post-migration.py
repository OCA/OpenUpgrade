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

defaults_force = {
    'hr_timesheet_sheet.sheet':
        [('company_id', None)],
    }
   
def set_timesheet_employee(cr, pool):
    """
    Migrate timesheet owner by user to employee. 
    """
    sheet_pool = pool.get('hr_timesheet_sheet.sheet')
    cr.execute("""
        SELECT
            hr_timesheet_sheet_sheet.id,
            hr_employee.id
        FROM
            hr_timesheet_sheet_sheet,
            hr_employee
        WHERE
            hr_timesheet_sheet_sheet.employee_id IS NULL
            AND hr_timesheet_sheet_sheet.openupgrade_legacy_user_id IS NOT NULL
            AND hr_employee.openupgrade_legacy_user_id = hr_timesheet_sheet_sheet.openupgrade_legacy_user_id
        """)
    for row in cr.fetchall():
        sheet_pool.write(
            cr, 1, [row[0]], {'employee_id': row[1]})

@openupgrade.migrate()
def migrate(cr, version):
    pool = pooler.get_pool(cr.dbname)
    openupgrade.set_defaults(cr, pool, defaults_force, force=True)
    set_timesheet_employee(cr, pool)
