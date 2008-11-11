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
import wizard
import netsvc
import pooler
import time
from osv import fields, osv

import datetime
import math

form = """<?xml version="1.0"?>
<form string="Create Timesheet Line">
    <field name="grant" colspan="4"/>
    <newline/>
    <field name="date1"/>
    <field name="date2"/>
</form>
"""
fields = {
  'grant': {'string': 'Grants', 'type': 'many2many', 'relation': 'cci_timesheet.grant', 'required': True},
  'date1': {'string': 'Date1','type': 'datetime','required': False},
  'date2': {'string': 'Date2','type': 'datetime','required': False},
          }

def conv_hours(value, date):
     minutes,hours = math.modf(value)
     minutes = int(minutes*100)
     hours = int(hours)
     if minutes:
          minutes = (minutes*60)/100
     b = (hours,minutes)
     time_format = "%Y-%m-%d %H:%M:%S"
     d = time.strptime(date,time_format)
     c = datetime.timedelta(hours=d[3],minutes=d[4]) + datetime.timedelta(hours=b[0],minutes=b[1])
     if c.days > 0:
         c = datetime.timedelta(seconds=c.seconds)
     return c

def create_lines(self, cr, uid, data, context):
    pool_obj=pooler.get_pool(cr.dbname)
    case_obj = pool_obj.get('crm.case')
    work_obj = pool_obj.get('project.task.work')
    list_temp = []

    list_temp.append(('grant_id','in',data['form']['grant'][0][2]))
    if data['form']['date1']:
        list_temp.append(('date','>=',data['form']['date1']))
    if data['form']['date2']:
        list_temp.append(('date','<=',data['form']['date2']))
    ids_meeting = case_obj.search(cr, uid, list_temp)
    ids_task_work = work_obj.search(cr, uid, list_temp)
    data_meeting = case_obj.browse(cr, uid, ids_meeting)
    data_task_work = work_obj.browse(cr, uid, ids_task_work)
    time_format = "%Y-%m-%d %H:%M:%S"
    for meeting in data_meeting:
        if not meeting.timesheet_line_id:
            to = conv_hours(meeting.duration, meeting.date)
            frm = time.strptime(meeting.date,time_format)
            frm1 = datetime.timedelta(hours=frm[3],minutes=frm[4])
            hour_from = '.'.join(str(frm1).split(':')[:2])
            hour_to = '.'.join(str(to).split(':')[:2])
            vals = { 'name':meeting.name,
                     'grant_id':meeting.grant_id.id,
                     'user_id':meeting.user_id.id,
                     'day_date':meeting.date,
                     'partner_id':meeting.partner_id.id,
                     'hour_from':hour_from,
                     'hour_to':hour_to,
                     'zip_id':meeting.zip_id.id,
            }
            id_line = pool_obj.get('cci_timesheet.line').create(cr, uid, vals)
            case_obj.write(cr, uid, meeting.id, {'timesheet_line_id':id_line})
    for task in data_task_work:
        if not task.timesheet_line_id:
            to = conv_hours(task.hours, task.date)
            frm = time.strptime(task.date,time_format)
            frm1 = datetime.timedelta(hours=frm[3],minutes=frm[4])
            hour_from = '.'.join(str(frm1).split(':')[:2])
            hour_to = '.'.join(str(to).split(':')[:2])
            vals = { 'name':task.name,
                     'grant_id':task.grant_id.id,
                     'user_id':task.user_id.id,
                     'day_date':task.date,
                     'partner_id':task.partner_id.id,
                     'hour_from':hour_from,
                     'hour_to':hour_to,
                     'zip_id':task.zip_id.id,
            }
            id_line1 = pool_obj.get('cci_timesheet.line').create(cr, uid, vals)
            work_obj.write(cr, uid, [task.id] , {'timesheet_line_id':id_line1})
    return {}
class create_timesheet_lines(wizard.interface):
    states = {
        'init' : {
               'actions' : [],
               'result': {'type': 'form', 'arch': form, 'fields': fields, 'state':[('end','Cancel'),('open','Create lines')]}
            },
        'open': {
            'actions': [create_lines],
            'result': {'type':'state', 'state': 'end'}
            },
    }
create_timesheet_lines("cci_timesheet.create_lines")
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

