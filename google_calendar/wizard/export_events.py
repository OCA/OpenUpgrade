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

import time
import datetime

from gdata import service
import gdata.calendar.service
import gdata.calendar
import atom

import wizard
import pooler
from osv import fields, osv

_google_form =  '''<?xml version="1.0"?>
        <form string="Export">
        <separator string="Export events to google calendar " colspan="4"/>
        <field name="event_id" domain = "[('user_id','=', uid)]" height="300" width="700" nolabel="1" required="True"/>
        </form> '''

_google_fields = {
        'event_id': {'string': 'Export ', 'type': 'many2many', 'relation':'event.event'},
        }

class google_calendar_wizard(wizard.interface):

    calendar_service = ""

    def add_event(self, calendar_service, title='',content='', where='', start_time=None, end_time=None):
        event = gdata.calendar.CalendarEventEntry()
        event.title = atom.Title(text=title)
        event.content = atom.Content(text=content)
        event.where.append(gdata.calendar.Where(value_string=where))
        time_format = "%Y-%m-%d %H:%M:%S"
        if start_time:
            # convert event start date into gmtime format
            timestring = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(time.mktime(time.strptime(start_time, "%Y-%m-%d %H:%M:%S"))))
            starttime = time.strptime(timestring, time_format)
            start_time = time.strftime('%Y-%m-%dT%H:%M:%S.000Z', starttime)
        if end_time:
            # convert event end date into gmtime format
            timestring_end = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(time.mktime(time.strptime(end_time, "%Y-%m-%d %H:%M:%S"))))
            endtime = time.strptime(timestring_end, time_format)
            end_time = time.strftime('%Y-%m-%dT%H:%M:%S.000Z', endtime)

        if start_time is None:
          # Use current time for the start_time and have the event last 1 hour
          start_time = time.strftime('%Y-%m-%dT%H:%M:%S.000Z', time.gmtime())
          end_time = time.strftime('%Y-%m-%dT%H:%M:%S.000Z', time.gmtime(time.time() + 3600))
        event.when.append(gdata.calendar.When(start_time=start_time, end_time=end_time))

        new_event = calendar_service.InsertEvent(event, '/calendar/feeds/default/private/full')
        return new_event

    def _export_events(self, cr, uid, data, context):
        # To do: 1. using proxy connect
        #        2. both side synchronize
        #        3. some events in the calendar (crm) are linked to section that should be synchronized with google calendar
        #        4. time zone for time of event start and end / gmtime
        #        5. open summary window after finish exporting
        obj_user = pooler.get_pool(cr.dbname).get('res.users')
        google_auth_details = obj_user.browse(cr, uid, uid)
        location = google_auth_details.company_id.partner_id.address[0].city #should be check

        if not google_auth_details.google_email or not google_auth_details.google_password:
            raise osv.except_osv('Warning !',
                                 'Please Enter google email id and password in users')
        try:
            self.calendar_service = gdata.calendar.service.CalendarService()
            self.calendar_service.email = google_auth_details.google_email
            self.calendar_service.password = google_auth_details.google_password
            self.calendar_service.source = 'Tiny'
            self.calendar_service.ProgrammaticLogin()
            obj_event = pooler.get_pool(cr.dbname).get('event.event')
            data_event = obj_event.read(cr, uid, data['form']['event_id'][0][2], [])
            for event in data_event:
                self.add_event(self.calendar_service, event['name'], event['name'], location, event['date_begin'], event['date_end'])
            return {}
        except Exception, e:
            raise osv.except_osv('Error !', e )

    states = {
        'init': {
            'actions': [],
            'result': {'type': 'form', 'arch':_google_form, 'fields':_google_fields,  'state':[('end','Cancel'),('export','Export to Calendar')]}
        },
        'export': {
            'actions': [_export_events],
            'result': {'type': 'state', 'state': 'end'}
        }
    }

google_calendar_wizard('google.calendar')