# -*- encoding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2005-2006 TINY SPRL. (http://tiny.be) All Rights Reserved.
#
# $Id: hr.py 4656 2006-11-24 09:58:42Z ced $
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsability of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# garantees and support are strongly adviced to contract a Free Software
# Service Company
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
##############################################################################

from mx import DateTime
import time

from osv import fields, osv

class hr_employee_salary_allowance(osv.osv):
    _name = "hr.employee.salary.allowance"
    _description = "Employee Allowances"
    _columns = {
                'allowance_id': fields.many2one('hr.employee', 'Allowance', select=True),
        'name' : fields.char('Allowance', size=32, required=True),
                'value' : fields.float('Value', digits=(16,2)),
                'taxable' : fields.boolean("Taxable"),
        }
    _order = 'name desc'
hr_employee_salary_allowance()

class hr_employee_salary_deduction(osv.osv):
    _name = "hr.employee.salary.deduction"
    _description = "Employee Deductions"
    _columns = {
                'deduction_id': fields.many2one('hr.employee', 'Deduction', select=True),
        'name' : fields.char('Deduction', size=32, required=True),
                'value' : fields.float('Value', digits=(16,2)),
                'remark' : fields.text('Remark'),
        }
    _order = 'name desc'
hr_employee_salary_deduction()

class hr_employee_salary_declaration(osv.osv):
    _name = "hr.employee.salary.declaration"
    _description = "Employee Tax Declarations"
    _columns = {
                'declaration_id': fields.many2one('hr.employee', 'Declaration', select=True),
        'name' : fields.char('Description', size=32, required=True),
                'value' : fields.float('Value', digits=(16,2)),
                'remark' : fields.text('Remark'),
        }
    _order = 'name desc'
hr_employee_salary_declaration()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

