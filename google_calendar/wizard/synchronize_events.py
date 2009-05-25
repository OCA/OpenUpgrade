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
from dateutil.tz import *
from dateutil.parser import *
from pytz import timezone
import pytz

from gdata import service
import gdata.calendar.service
import gdata.calendar
import atom

import wizard
import pooler
from osv import fields, osv

_google_form =  '''<?xml version="1.0"?>
        <form string="Export">
        <separator string="This wizard synchronize events between tiny and google calendar" colspan="4"/>
        </form> '''

_google_fields = {
        }

_timezone_form =  '''<?xml version="1.0"?>
        <form string="Export">
        <separator string="Select Timezone" colspan="4"/>
        <field name="timezone_select"/>
        </form> '''

_timezone_fields = {
            'timezone_select': {
            'string': 'Time Zone',
            'type': 'selection',
            'selection': [(x, x) for x in pytz.all_timezones],
            'required': True,
        },
        }

_timezone_form =  '''<?xml version="1.0"?>
        <form string="Export">
        <separator string="Select Timezone" colspan="4"/>
        <field name="timezone_select"/>
        </form> '''

_timezone_fields = {
            'timezone_select': {
            'string': 'Time Zone',
            'type': 'selection',
            'selection': [(x, x) for x in pytz.all_timezones],
            'required': True,
        },
        }


def _tz_get(self, cr, uid, data, context={}):
    if 'tz' in context and context['tz']:
        return 'synch'
    else:
        return 'timezone'


class google_calendar_wizard(wizard.interface):

    calendar_service = ""

    def add_event(self, calendar_service, title='',content='', where='', start_time=None, end_time=None):

        try:
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
        except Exception, e:
            raise osv.except_osv('Error !', e )

    def _synch_events(self, cr, uid, data, context={}):

#        To do import:
#            - Retrieving events without query parameters => done
#            - Retrieving events for a specified date range
#            - all events should be retrieve currently it comes with limit (25)
#            - more attribute can be added if possible on event.event
#            - open summary window after finish importing
#            - delete events

#         To do export:
#            1. using proxy connect
#            2. open summary window after finish exporting
#            3. multiple location of events
#            4. delete events

        obj_user = pooler.get_pool(cr.dbname).get('res.users')
        product = pooler.get_pool(cr.dbname).get('product.product').search(cr, uid, [('name', 'like', 'Calendar Product')])
        google_auth_details = obj_user.browse(cr, uid, uid)
        obj_event = pooler.get_pool(cr.dbname).get('event.event')
        if not google_auth_details.google_email or not google_auth_details.google_password:
            raise osv.except_osv('Warning !',
                                 'Please Enter google email id and password in users')
        if 'tz' in context and context['tz']:
            time_zone = context['tz']
        else:
            time_zone = data['form']['timezone_select']
        au_tz = timezone(time_zone)
        try :
            self.calendar_service = gdata.calendar.service.CalendarService()
            self.calendar_service.email = google_auth_details.google_email
            self.calendar_service.password = google_auth_details.google_password
            self.calendar_service.source = 'Tiny'
            self.calendar_service.max_results = 500 # to be check
            self.calendar_service.ProgrammaticLogin()
            tiny_events = obj_event.search(cr, uid, [])
            city = google_auth_details.company_id.partner_id.address[0].city or ''
            street =  google_auth_details.company_id.partner_id.address[0].street or ''
            street2 = google_auth_details.company_id.partner_id.address[0].street2 or ''
            zip = google_auth_details.company_id.partner_id.address[0].zip or ''
            country = google_auth_details.company_id.partner_id.address[0].country_id.name or ''
            location = street + " " +street2 + " " + city + " " + zip + " " + country
            tiny_events = obj_event.browse(cr, uid, tiny_events)
            feed = self.calendar_service.GetCalendarEventFeed()
            tiny_event_dict = {}
            for event in tiny_events:
                if not event.google_event_id:
                    new_event = self.add_event(self.calendar_service, event.name, event.name, location, event.date_begin, event.date_end)
                    obj_event.write(cr, uid, [event.id], {'google_event_id': new_event.id.text,
                       'event_modify_date': new_event.updated.text #should be correct!
                       })
                    tiny_event_dict[event.google_event_id] = event
                tiny_event_dict[event.google_event_id] = event
            for i, an_event in enumerate(feed.entry):
                google_id = an_event.id.text
                if google_id in tiny_event_dict.keys():
                    event = tiny_event_dict[google_id]
                    google_up = an_event.updated.text # google event modify date
                    utime = dateutil.parser.parse(google_up)
                    au_dt = au_tz.normalize(utime.astimezone(au_tz))
                    timestring_update = datetime.datetime(*au_dt.timetuple()[:6]).strftime('%Y-%m-%d %H:%M:%S')
                    google_up = timestring_update
                    tiny_up = event.event_modify_date # Tiny google event modify date
                    if event.write_date > google_up:
                        # tiny events => google
                        an_event.title.text = event.name
                        an_event.content.text = event.name
                        an_event.where.insert(0, gdata.calendar.Where(value_string=location))
                        time_format = "%Y-%m-%d %H:%M:%S"
                        # convert event start date into gmtime format
                        timestring = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(time.mktime(time.strptime(event.date_begin, "%Y-%m-%d %H:%M:%S"))))
                        starttime = time.strptime(timestring, time_format)
                        start_time = time.strftime('%Y-%m-%dT%H:%M:%S.000Z', starttime)
                        # convert event end date into gmtime format
                        timestring_end = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(time.mktime(time.strptime(event.date_end, "%Y-%m-%d %H:%M:%S"))))
                        endtime = time.strptime(timestring_end, time_format)
                        end_time = time.strftime('%Y-%m-%dT%H:%M:%S.000Z', endtime)
                        an_event.when[0].start_time = start_time
                        an_event.when[0].end_time = end_time
                        update_event = self.calendar_service.UpdateEvent(an_event.GetEditLink().href, an_event)

                    elif event.write_date < google_up:
                        # google events => tiny
                        utime = dateutil.parser.parse(an_event.updated.text)
                        au_dt = au_tz.normalize(utime.astimezone(au_tz))
                        timestring_update = datetime.datetime(*au_dt.timetuple()[:6]).strftime('%Y-%m-%d %H:%M:%S')
                        name_event = an_event.title.text or ''
                        stime = an_event.when[0].start_time
                        etime = an_event.when[0].end_time
                        stime = dateutil.parser.parse(stime)
                        etime = dateutil.parser.parse(etime)
                        try:
                            au_dt = au_tz.normalize(stime.astimezone(au_tz))
                            timestring = datetime.datetime(*au_dt.timetuple()[:6]).strftime('%Y-%m-%d %H:%M:%S')
                            au_dt = au_tz.normalize(etime.astimezone(au_tz))
                            timestring_end = datetime.datetime(*au_dt.timetuple()[:6]).strftime('%Y-%m-%d %H:%M:%S')
                        except :
                            timestring = datetime.datetime(*stime.timetuple()[:6]).strftime('%Y-%m-%d %H:%M:%S')
                            timestring_end = datetime.datetime(*etime.timetuple()[:6]).strftime('%Y-%m-%d %H:%M:%S')
                        val = {
                           'name': name_event,
                           'date_begin': timestring,
                           'date_end': timestring_end,
                           'event_modify_date': timestring_update
                           }
                        obj_event.write(cr, uid, [event.id], val)

                    elif event.write_date == google_up:
                        pass

                else:
                    google_id = an_event.id.text
                    utime = dateutil.parser.parse(an_event.updated.text)
                    au_dt = au_tz.normalize(utime.astimezone(au_tz))
                    timestring_update = datetime.datetime(*au_dt.timetuple()[:6]).strftime('%Y-%m-%d %H:%M:%S')
                    name_event = an_event.title.text or ''
                    stime = an_event.when[0].start_time
                    etime = an_event.when[0].end_time
                    stime = dateutil.parser.parse(stime)
                    etime = dateutil.parser.parse(etime)
                    try :
                        au_dt = au_tz.normalize(stime.astimezone(au_tz))
                        timestring = datetime.datetime(*au_dt.timetuple()[:6]).strftime('%Y-%m-%d %H:%M:%S')
                        au_dt = au_tz.normalize(etime.astimezone(au_tz))
                        timestring_end = datetime.datetime(*au_dt.timetuple()[:6]).strftime('%Y-%m-%d %H:%M:%S')
                    except :
                        timestring = datetime.datetime(*stime.timetuple()[:6]).strftime('%Y-%m-%d %H:%M:%S')
                        timestring_end = datetime.datetime(*etime.timetuple()[:6]).strftime('%Y-%m-%d %H:%M:%S')
                    val = {
                       'name': name_event,
                       'date_begin': timestring,
                       'date_end': timestring_end,
                       'product_id': product[0],
                       'google_event_id': an_event.id.text,
                       'event_modify_date': timestring_update
                        }
                    obj_event.create(cr, uid, val)

            return {}
        except Exception, e:
            raise osv.except_osv('Error !', e )

    states = {
        'init': {
            'actions': [],
            'result': {'type': 'form', 'arch': _google_form, 'fields': _google_fields, 'state': [('end', 'Cancel'),('tz', 'Synchronize')]}
        },

        'tz': {
            'actions': [],
            'result': {'type': 'choice', 'next_state': _tz_get }
            },

        'timezone': {
            'actions': [],
            'result': {'type': 'form', 'arch': _timezone_form, 'fields': _timezone_fields, 'state': [('synch', 'Synchronize')]}
        },

        'synch': {
            'actions': [_synch_events],
            'result': {'type': 'state', 'state': 'end'}
        }
    }

google_calendar_wizard('google.calendar.synch')

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
