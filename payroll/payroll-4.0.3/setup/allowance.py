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

class payroll_salary_allowance(osv.osv):
    _name = "payroll.salary.allowance"
    _description = "Allowance Type"
    _columns = {
            'name' : fields.char('Allowance Name', size=32, required=True),
            'description' : fields.char('Description', size=32, required=True),
            'percent' : fields.float('Per cent of basic salary', digits=(16,2), required=True),
            'taxable' : fields.boolean("Taxable"),
            'attendance' : fields.boolean("Attendance Specific"),
            'periodicity' : fields.boolean("Monthly Variable"),
            'prec' : fields.float('Precision', digits=(16,2), required=True),
        }
    _defaults = {
            'percent': lambda *a: 0.0,
            'prec': lambda *a: 1.0,
            'attendance' : lambda *a: True,
        }
    _order = 'name desc'
    def onchange_percent(self, cr, uid, ids, percent):
            for id in ids:
                result = {'value': False, 'cal_value': False, 'name': False}
                basic = 0.0
                #percent = 0.0
                val = 0.0
                th = self.browse(cr, uid, id)
                all_pool = self.pool.get('hr.employee.salary.allowance')
                alls = all_pool.search(cr, uid, [('allowance_type','=',id)])
                for all in alls:
                    this = all_pool.browse(cr, uid, all)
                    if this.employee_id.id:
                        emp = self.pool.get('hr.employee').browse(cr, uid, this.employee_id.id)
                        basic = emp.basic
                        val = (basic*percent)/100
                        result['value'] = val
                        result['cal_value'] = val
                        result['name'] = th.name
                        print result
                        all_pool.write(cr, uid, [all], result)
            return {}
payroll_salary_allowance()


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

