# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution    
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>). All Rights Reserved
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

from osv import osv, fields
import pooler
from copy import deepcopy
 
class wizard_hr_holidays_evaluation(osv.osv_memory):
   
    _name='wizard.hr.holidays.evaluation'
    _rec_name = 'holiday_status_id'

    _columns = {
        'holiday_status_id':fields.many2one('hr.holidays.status','Holiday Status', required=True),
        'hr_timesheet_group_id':fields.many2one('hr.timesheet.group', 'Timesheet Group', required=True),
        'float_time':fields.float('Minutes', required=True)
    }

    
    def action_create(self, cr, uid, ids, context=None):
         temp=0.0
         count = 0
         obj_contract = self.pool.get('hr.contract')
         obj_self = self.browse(cr, uid, ids, context=context)[0]
         group_ids = obj_self.hr_timesheet_group_id.name
         obj_ids = obj_contract.search(cr, uid, [('working_hours_per_day_id', '=', group_ids)]) 
         for rec_con in obj_contract.browse(cr,uid,obj_ids):
             name=rec_con.employee_id.id
             s_date = rec_con.date_start
             e_date = rec_con.date_end
             
             cr.execute("select htss.id from hr_timesheet_sheet_sheet as htss LEFT JOIN hr_attendance as ha ON htss.id = ha.id where htss.date_current >= %s and htss.date_current <= %s and ha.employee_id = %s", (s_date,e_date,name))
             vv = cr.fetchall()
             sheet_ids = map(lambda x: x[0], vv)
             days=len(sheet_ids)
             
#             for i in sheet_ids:
#                 sheet_obj = self.pool.get('hr_timesheet_sheet.sheet').browse(cr, uid, [i])[0]
#                 hrs = sheet_obj.total_attendance_day
#                 if hrs > 0:
#                     count += 1
#                 temp+=hrs

             mins = days * obj_self.float_time
         return {}
         
    def action_cancel(self,cr,uid,ids,context=None):
        return {}

wizard_hr_holidays_evaluation()




# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: