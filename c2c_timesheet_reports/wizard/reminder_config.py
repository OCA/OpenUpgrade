# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) Camptocamp SA
# Author: Arnaud Wüst
#
#
#    This file is part of the c2c_timesheet_report module
#
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

import wizard
#from copy import copy
import pooler
import time




_form = '''<?xml version="1.0"?>
    <form string="Timesheet reminder Configuration" width="400">
        <group colspan="4" col="4" string="Periodicity">
            <field name="reminder_active" />        
            <newline/>
            <field name="nextcall" />
            <newline/>
            <field name="interval_number" string="Then send message every" />
            <field name="interval_type" nolabel="1" />
        </group>

        <group colspan="4" col="2" string="Message">
            <field name="reply_to" />
            <field name="subject"/>        
            <field name="message" height="200"/>        
        </group>
    </form>'''


_confirm_form = '''<?xml version="1.0"?>
    <form string="Timesheet reminder Run" >
        <separator string="The message has been sent" colspan="4"/>
    </form>'''
    
_confirm_fields = {}


_fields = {
        'reminder_active': {'string':'Reminder Active', 'type':'boolean'}, 
        'interval_type': {'string':'Periodicity Unit', 'type':'selection', 'selection':[('days','Day(s)'), ('weeks', 'Week(s)'), ('months', 'Month(s)')] }, 
        'interval_number': {'string':'Periodicity Quantity', 'type':'integer'}, 
        'nextcall': {'string':'Next Run', 'type':'datetime'},
        'message': {'string':'Message', 'type':'text' },
        'subject': {'string':'Subject', 'type':'char', 'size':200 },
        'reply_to': {'string':'Reply To', 'type':'char', 'size':100},
        }





def save_values(self, cr, uid, data, context):
    """ save defined settings in db """
 
    
    #retrieve the default cron values
    reminder = pooler.get_pool(cr.dbname).get('c2c_timesheet_reports.reminder')
    cron = reminder.cron
 
    #############
    # init and retrieve values from the form
    #############
    
    form= {}
    if 'form' in data:
        form = data['form']
    
    reminder_active = cron['active'] #default val
    if 'reminder_active' in form:
        reminder_active = form['reminder_active'] == 1
        
    interval_number = cron['interval_number'] # default val
    if 'interval_number' in form:
        interval_number = int(form['interval_number'])
    if interval_number < 1:
        interval_number = 1
        
    interval_type = cron['interval_type'] #default val
    if 'interval_type' in form:
        interval_type = form['interval_type']
    
    nextcall = cron['nextcall']
    if 'nextcall' in form:
        nextcall = form['nextcall']
    
    reply_to = ""
    if 'reply_to' in form:
        reply_to = form['reply_to']
    
    message = ""
    if 'message' in form:
        message = form['message']
    
    subject = ""
    if 'subject' in form:
        subject = form['subject']
    
    ##################
    ## save values in cron and in values
    ##################
    save_data = { 'reminder_active': reminder_active, 
                  'nextcall': nextcall,
                  'interval_number': interval_number, 
                  'interval_type': interval_type, 
                  'reply_to': reply_to, 
                  'message': message, 
                  'subject': subject,
                 }
    reminder.save_config(cr, uid, save_data, context)    
    return {}

    
def get_values(self, cr, uid, data, context):
    """ retrieve settings from db """
    
    #retrieve the default cron values
    reminder = pooler.get_pool(cr.dbname).get('c2c_timesheet_reports.reminder')   
    result = reminder.get_config(cr, uid, context)
    return result


def run(self, cr, uid, data, context):
    """ execute the timesheets check and send emails """
    reminder = pooler.get_pool(cr.dbname).get('c2c_timesheet_reports.reminder')
    reminder.run(cr, uid)
    return {}


class wiz_reminder_config(wizard.interface):
    

    states = {
        'init' : {
            'actions' : [get_values], 
            'result' : {'type':'form', 'arch':_form, 'fields':_fields, 'state': [('run', 'Save And Run Now'), ('save','Save'), ('end','Close')]},
        },
        'save': {
            'actions' : [save_values], 
            'result' : {'type':'state', 'state':'init'},
        },               
        'run': {
            'actions' : [save_values, run], 
            'result' : {'type': 'form', 'arch':_confirm_form, 'fields':_confirm_fields, 'state': [('init', 'Back'), ('end', 'Close')]},
        },               
    }
    
    
    
wiz_reminder_config('reminder_config')
