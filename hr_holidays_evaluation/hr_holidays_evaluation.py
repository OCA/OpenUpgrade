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
from mx import DateTime
import time
import datetime

from osv import osv, fields
import pooler

class hr_holidays_note(osv.osv):
    _name='hr.holidays.note'
    _description = "Holidays note"
    _rec_name = 'date'
    _order = 'date desc'

    def _compute_diff(self, cr, uid, ids, name, arg, context={}):
        res={}
        for id in ids:
            tmp = self.read(cr, uid, id, ['prev_number','new_number'])
            old, new = tmp['prev_number'], tmp['new_number']
            if not old:
                old = 0
            res[id] = new - old
        return res


    _columns = {
        'holiday_per_user_id':fields.many2one('hr.holidays','Holiday Status', required=True),
        'date' : fields.char('Date', size=64, required=True),
        'employee_id': fields.related('holiday_per_user_id','user_id',type='many2one', relation='hr.employee', string='Employee Name'),
        'prev_number': fields.float('Previous Holiday Number'),
        'new_number': fields.float('New Holiday Number', required=True),
        'diff': fields.function(_compute_diff, method=True, string='Difference', type='float'),
    } 
hr_holidays_note()

class wizard_hr_holidays_evaluation(osv.osv_memory):
    _name = 'wizard.hr.holidays.evaluation'
    _rec_name = 'holiday_status_id'
    _columns = {
        'holiday_status_id':fields.many2one('hr.holidays.status','Holiday Status',required=True,help='This is where you specify the holiday type to synchronize. It will create the "holidays per employee" accordingly if necessary, or replace the value "Max leaves allowed" into the existing one.'),
        'hr_timesheet_group_id':fields.many2one('hr.timesheet.group','Timesheet Group',required=True,help='This field allow you to filter on only the employees that have a contract using this working hour.'),
        'float_time':fields.float('Time',required=True,help='''This time depicts the amount per day earned by an employee working a day.The computation is: total earned = time * number of working days'''),
        'date_current' : fields.date('Date',help='This field allow you to choose the date to use, for forecast matter e.g')
    }
    _defaults = {
        'date_current' : lambda *a: time.strftime('%Y-%m-%d'),
        }
    
    def action_create(self, cr, uid, ids, context=None):
        data = {}
        objs = []
        value = {}
        my_dict = {}
        bjs = []
        contract_obj = self.pool.get('hr.contract')
        evaluation_obj = self.browse(cr, uid, ids, context = context)[0]
        group_id = evaluation_obj.hr_timesheet_group_id.id
        contract_ids = contract_obj.search(cr, uid, [('working_hours_per_day_id', '=', group_id)])

        for contract in contract_obj.browse(cr,uid,contract_ids):
            emp_id = contract.employee_id.id
            start_date = contract.date_start

            cr.execute("""SELECT distinct(ht.dayofweek), sum(ht.hour_to - ht.hour_from) 
                        FROM hr_timesheet_group as htg, hr_timesheet as ht 
                        WHERE ht.tgroup_id = htg.id AND htg.id = %s 
                        GROUP BY ht.dayofweek""" %evaluation_obj.hr_timesheet_group_id.id)

            timesheet_grp = cr.fetchall()
            alldays = map(lambda x: x[0],timesheet_grp)
            nod = len(alldays)
            alltime = map(lambda x: x[1],timesheet_grp)
            how = 0
            for k in alltime:
                how += k
            hpd = how/nod

            cr.execute("""SELECT distinct(to_date(to_char(ha.name, 'YYYY-MM-dd'),'YYYY-MM-dd')) 

                        FROM hr_attendance ha, hr_attendance ha2 
                        WHERE ha.action='sign_in' 
                            AND ha2.action='sign_out' 
                            AND (to_date(to_char(ha.name, 'YYYY-MM-dd'),'YYYY-MM-dd'))=(to_date(to_char(ha2.name, 'YYYY-MM-dd'),'YYYY-MM-dd')) 
                            AND (to_date(to_char(ha.name, 'YYYY-MM-dd'),'YYYY-MM-dd') <= %s)  
                            AND (to_date(to_char(ha.name, 'YYYY-MM-dd'),'YYYY-MM-dd') >= %s) 
                            AND ha.employee_id = %s """, (evaluation_obj.date_current, start_date, emp_id))

            results = cr.fetchall()
            all_dates = map(lambda x: x[0],results)
            days = len(all_dates)
            hrss = days * evaluation_obj.float_time

            if hrss < hpd:
                x = 0
            else:
                day = hrss / hpd
                x = int(day)
                y = day - x
                if y >= 0.5:
                    x += 0.5
                    
            holiday_obj = self.pool.get('hr.holidays')
            holiday_ids = holiday_obj.search(cr, uid, [('employee_id', '=', emp_id),('holiday_status_id', '=', evaluation_obj.holiday_status_id.id)])
            if len(holiday_ids) == 0:
                old_leave = False
                data = {'employee_id': emp_id, 'holiday_status_id': evaluation_obj.holiday_status_id.id, 'number_of_days_temp' : x}
                holiday_id = holiday_obj.create(cr, uid, data, context)

            else:
                holiday_id = holiday_ids[0]
                old_leave = holiday_obj.browse(cr, uid, holiday_id, context).number_of_days_temp
                holidays = holiday_obj.write(cr, uid, [holiday_id], {'number_of_days_temp':x})

            value = {
                'date': str(DateTime.now()),
                'holiday_per_user_id': holiday_id,
                'prev_number': old_leave, 
                'new_number': x,
            }

            note_id = self.pool.get('hr.holidays.note').create(cr, uid, value, context)
            bjs.append(note_id)

        return {
            'domain': "[('id','in', ["+','.join(map(str,bjs))+"])]",
            'name': _('Summary Report'),
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'hr.holidays.note',
            'type': 'ir.actions.act_window'
            }
         
    def action_cancel(self,cr,uid,ids,context=None):
        return {}
    
wizard_hr_holidays_evaluation()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
