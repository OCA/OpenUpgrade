# -*- encoding: utf-8 -*-
import wizard
import netsvc
import pooler
import time
from osv import fields, osv

form = """<?xml version="1.0"?>
<form string="Timesheet Line">
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

def create_lines(self, cr, uid, data, context):
    pool_obj=pooler.get_pool(cr.dbname)
    ids_meeting = pool_obj.get('crm.case').search(cr, uid, [('grant_id','in',data['form']['grant'][0][2]), ('date','>=',data['form']['date1']), ('date','<=',data['form']['date2'])])
    ids_task_work = pool_obj.get('project.task.work').search(cr, uid, [('grant_id','in',data['form']['grant'][0][2]), ('date','>=',data['form']['date1']), ('date','<=',data['form']['date2'])])
    data_meeting = pool_obj.get('crm.case').browse(cr, uid, ids_meeting)
    data_task_work = pool_obj.get('project.task.work').browse(cr, uid, ids_task_work)
    for meeting in data_meeting:
        vals = { 'name':meeting.name,
                 'grant_id':meeting.grant_id.id,
                 'user_id':meeting.user_id.id,
                 'day_date':meeting.date,
                 'partner_id':meeting.partner_id.id,
                 'hour_from':'0.0',
                 'hour_to':'0.0',
                 'zip_id':meeting.zip_id.id,
        }
        pool_obj.get('cci_timesheet.line').create(cr, uid, vals)
    for task in data_task_work:
        vals = { 'name':task.name,
                 'grant_id':task.grant_id.id,
                 'user_id':task.user_id.id,
                 'day_date':task.date,
                 'partner_id':task.partner_id.id,
                 'hour_from':'0.0',
                 'hour_to':'0.0',
                 'zip_id':task.zip_id.id,
        }
        pool_obj.get('cci_timesheet.line').create(cr, uid, vals)
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

