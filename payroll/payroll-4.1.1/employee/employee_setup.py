# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution	
#    Copyright (C) 2004-2008 Tiny SPRL (<http://tiny.be>). All Rights Reserved
#    $Id$
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from mx import DateTime
import time

from osv import fields, osv

class employee_setup_payelements(osv.osv):
    _name = "employee.setup.payelements"
    _description = "Employee Pay Elements"
    _columns = {
        'employee_id': fields.many2one('hr.employee', 'Employee', select=True),
        'element_name' : fields.many2one("payroll.setup.payelements",'Element ID', required=True),
        'element_type' : fields.selection([('payelements','PAY ELEMENT'),('deductions','DEDUCTION'),('reimbursements','REIMBURSEMENTS')], 'Category', readonly=True),
        'name' : fields.char('Description', size=32, readonly=True),
        #'element_specific' : fields.boolean("Pay Element Specific"),
        #'taxable' : fields.boolean("Taxable"),
        #'attendance' : fields.boolean("Attendance Specific"),
        #'monthly_variable' : fields.boolean("Monthly Variable"),
        #'emp_wise_posting' : fields.boolean("Employee Wise Posting"),
        'dependent_on' : fields.many2one("payroll.setup.payelements", "Dependent on"),
        'formulae' : fields.selection([('percent','PERCENT'),('addition','ADDITION'),('subtraction','SUBTRACTION'),('multiplication','MULTIPLICATION')], 'Formulae'),
        'value' : fields.float("Value", digits=(12,2)),
        'cal_value' : fields.float("Calculated Value", digits=(12,2)),
        'arrier' : fields.float("Arrear", digits=(12,2)),
        'incr' : fields.one2many('employee.specify.increment', 'name', 'Increment'),
        'incr_date' : fields.date("Increment date"),
        }
    _defaults = {
        'cal_value' : lambda *a: -1,
        }
    _order = 'name desc'
    def onchange_payelements(self, cr, uid, ids, element_name):
                result = {'value': {'value': False, 'dependent_on':False, 'formulae': False, 'name': False, 'element_type': False}}
                if element_name:
                    payelement = self.pool.get('payroll.setup.payelements').browse(cr, uid, element_name)
                    if payelement.dependent_on:
                        result['value']['dependent_on'] = payelement.dependent_on.id
                    if payelement.value:
                        result['value']['value'] = payelement.value
                    if payelement.formulae:
                        result['value']['formulae'] = payelement.formulae
                    if payelement.description:
                        result['value']['name'] = payelement.description
                    if payelement.element_type:
                        result['value']['element_type'] = payelement.element_type
                return result
            
employee_setup_payelements()

class employee_specify_increment(osv.osv):
    _name = "employee.specify.increment"
    _description = "Employee increment section"
    
    _columns = {
        'name' : fields.many2one('hr.employee', 'Employee name'),
        'incr_date' : fields.date('Increment date'),
        'component' : fields.many2one('employee.setup.payelements', 'Component'),
        'description' : fields.char('Description', size=32),
        'amount' : fields.float('Amount', digits=(12,2)),
        'aplicable' : fields.boolean('Applicable'),
        'status' : fields.selection([('pending','Pending'),('done','Done')], 'Status'),
        'arrear' : fields.float('Arrear', digits=(12,2) ),
    }
    _defaults = {
        'status' : lambda *a: 'pending',
    }
    def increment_apply(self, cr, uid, ids, context={}):
        incrs = self.browse(cr, uid, ids)
        for incr in incrs:
            incr_dt = incr.incr_date
            incr_dt = incr_dt.split('-')
            incr_mnths = int(incr_dt[0])*12 + int(incr_dt[1])
            curr_dt = time.gmtime()
            curr_mnths = curr_dt[0]*12 + curr_dt[1]
            diff_mnths = curr_mnths - incr_mnths
            arrear = 0
            if diff_mnths > 0:
                arrear = incr.amount * diff_mnths
            self.write(cr, uid, ids, {'arrear':arrear} )
        return True
employee_specify_increment()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

