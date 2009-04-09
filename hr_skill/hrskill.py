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
from osv import fields,osv


def _currency_get(self, cr, uid, context={}):
        obj = self.pool.get('res.currency')
        ids = obj.search(cr, uid, [])
        res = obj.read(cr, uid, ids, ['code','name'], context)
        return [(r['code'],r['name']) for r in res]

def _status_get(self, cr, uid, context={}):
        obj = self.pool.get('employee.status')
        ids = obj.search(cr, uid, [])
        res = obj.read(cr, uid, ids, ['name'], context)
        return [(r['name'],r['name']) for r in res]

class hr_lang(osv.osv):
    _description ='Languages'
    _name = 'hr.lang'
    _columns = {

        'name':fields.char('Language',size=64),
              }
hr_lang()

class emp_lang(osv.osv):
    _description ='Languages'
    _name = 'emp.lang'
    _columns = {
        'ii_id': fields.many2one('hr.employee','languages known'),
        'name':fields.many2one('hr.lang','Language'),
        'read': fields.boolean('Read'),
        'write': fields.boolean('Write'),
        'speak': fields.boolean('Speak'),
        }
emp_lang()

class hr_scale(osv.osv):
    _description ='Pay Scales'
    _name='hr.scale'

    _columns = {
         'code' : fields.char('Code', size=64,),
         'name' : fields.char('Name', size=64),
         'cur' : fields.selection(_currency_get, 'Currency', method=True),
         'min_sal' : fields.integer('Minimum Salary'),
         'max_sal' : fields.integer('Maximum Salary'),
         'increase' : fields.integer('Step Increase'),

                }
hr_scale()

class hr_employee(osv.osv):
    _description ='Employees'
    _name='hr.employee'
    _inherit='hr.employee'
    _columns = {
         'lang_id':fields.one2many('emp.lang','ii_id','Languages Known'),
         'leavedate' : fields.date('Leaved on'),
         'status' : fields.selection(_status_get, 'Employee Status', method=True,),
         'payscale':fields.many2one('hr.scale','Scale'),
        }
hr_employee()

class employee_status(osv.osv):
    _name = 'employee.status'
    _columns = {
                'name' : fields.char('Status Name', size=128, required=True)
               }
employee_status()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

