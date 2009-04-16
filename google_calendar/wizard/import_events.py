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
import dateutil
from dateutil import parser

from gdata import service
import gdata.calendar.service
import gdata.calendar
import atom

import wizard
import pooler
from osv import fields, osv

_google_form =  '''<?xml version="1.0"?>
        <form string="Import">
        <separator string="Import events from google calendar " colspan="4"/>
        </form> '''

_google_fields = {
        }

class google_calendar_wizard(wizard.interface):

    calendar_service = ""

    def _import_events(self, cr, uid, data, context):
        obj_user = pooler.get_pool(cr.dbname).get('res.users')
        product = pooler.get_pool(cr.dbname).get('product.product').search(cr, uid, [('name', 'like', 'Calendar Product')])
        google_auth_details = obj_user.browse(cr, uid, uid)
        obj_event = pooler.get_pool(cr.dbname).get('event.event')

#        To do:
#            - Retrieving events without query parameters => done
#            - Retrieving events for a specified date range
#            - all events should be retrieve curretly it comes with limit (25)
#            - time zone set
#            - set start and end date of event from calendar of google using rfc3339 format => done
#            - more attribute can be added if possible on event.event
#            - open summary window after finish importing

        if not google_auth_details.google_email or not google_auth_details.google_password:
            raise osv.except_osv('Warning !',
                                 'Please Enter google email id and password in users')
        try:
            self.calendar_service = gdata.calendar.service.CalendarService()
            self.calendar_service.email = google_auth_details.google_email
            self.calendar_service.password = google_auth_details.google_password
            self.calendar_service.source = 'Tiny'
            self.calendar_service.max_results = 500
            self.calendar_service.ProgrammaticLogin()
            feed = self.calendar_service.GetCalendarEventFeed()
#            feed.timezone.value = 'Asia/Calcutta'
            for i, an_event in enumerate(feed.entry):
                name_event = an_event.title.text or ''
                stime = an_event.when[0].start_time
                etime = an_event.when[0].end_time

                from dateutil.tz import *
                stime = dateutil.parser.parse(stime)
                etime = dateutil.parser.parse(etime)
                start_date = datetime.datetime(*stime.timetuple()[:6]).strftime('%Y-%m-%d %H:%M:%S')
                end_date = datetime.datetime(*etime.timetuple()[:6]).strftime('%Y-%m-%d %H:%M:%S')

                a = time.mktime(time.strptime(start_date, "%Y-%m-%d %H:%M:%S"))
                timestring = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(a - time.timezone - 30600))

                b = time.mktime(time.strptime(end_date, "%Y-%m-%d %H:%M:%S"))
                timestring_end = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(b - time.timezone - 30600))


                val = {
                   'name': name_event,
                   'date_begin': timestring,#start_date,
                   'date_end': timestring_end,#end_date,
                   'product_id': product[0]
                       }
                obj_event.create(cr, uid, val)
            return {}

        except Exception, e:
            raise osv.except_osv('Error !', e )

    states = {
        'init': {
            'actions': [],
            'result': {'type': 'form', 'arch':_google_form, 'fields':_google_fields,  'state':[('end','Cancel'),('import','Import events')]}
        },
        'import': {
            'actions': [_import_events],
            'result': {'type': 'state', 'state': 'end'}
        }
    }

google_calendar_wizard('google.calendar.import')