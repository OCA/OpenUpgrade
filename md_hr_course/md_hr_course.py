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

class md_hr_course(osv.osv):
    _name="md.hr.course"
    _description="Course"
    _columns={
         'code' : fields.char("Code", size=16,required="True"),
         'name' : fields.char("Course title", size=16,required="True"),
        
        }
md_hr_course()

class md_hr_course_student(osv.osv):
    _name="md.hr.course.student"
    _description="Course Student"
    _columns={
        'employee_id':fields.many2one('hr.employee','Employee'),
        'course_id':fields.many2one('md.hr.course','Course'),
        'date':fields.date('Date followed'),
        'state':fields.selection([('draft','Draft'),('approved by manager','Approved by manager'),('approved by HR','Approved by HR'),('completed','Completed'),('canceled', 'Canceled')], 'State', select=True),
        'personal_contribution':fields.boolean('Personal Contribution'),
        'amount':fields.float('Amount'),
        'payback_clause':fields.float('Pay back clause (in %)'),
        'payback_clause_ends':fields.date('Pay back clause ends'),
        
        }
    def on_change_payback_clause(self,cr, uid, ids, payback_clause,context=None): 

        if payback_clause < 0.00 :
           raise osv.except_osv(
                            'Please Enter Value > 0 !!!!','Pay back clause (in %)')
           return {'value':{'payback_clause':0.00}}
        if payback_clause > 100.00:
          raise osv.except_osv(
                        'Please Enter Value < 100 !!!!','Pay back clause (in %)')
          return {'value':{'payback_clause':0.00}} 
        return {}
        
    
md_hr_course_student()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

