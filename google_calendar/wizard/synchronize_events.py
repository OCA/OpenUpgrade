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

_summary_form = '''<?xml version="1.0"?>
        <form string="Summary">
            <field name="summary" nolabel="1" height="300" width="800" />
        </form> '''

_summary_fields = {
            'summary': {'string': 'Summary', 'type': 'text', 'required': False, 'readonly': True},
        }

def _tz_get(self, cr, uid, data, context={}):
    if 'tz' in context and context['tz']:
        return 'synch'
    else:
        return 'timezone'

visibility_list = {
            'PRIVATE': 'private',
            'DEFAULT': 'default',
            'PUBLIC': 'public'
            }

def _get_privacy(self, privacy):
    if not privacy:
        return 'public'
    return visibility_list[privacy]

def _get_repeat_status(self, str_google, byday):
    if not str_google:
        return 'norepeat'
    if str_google == 'DAILY':
        return 'daily'
    elif str_google == 'YEARLY':
        return 'yearly'
    elif str_google == 'MONTHLY':
        return 'monthly'
    elif str_google == 'WEEKLY' and byday == 'MO,TU,WE,TH,FR':
        return 'everyweekday'
    elif str_google == 'WEEKLY' and byday == 'MO,WE,FR':
        return 'every_m_w_f'
    elif str_google == 'WEEKLY' and byday == 'TU,TH':
        return 'every_t_t'
    elif str_google == 'WEEKLY':
        return 'weekly'
    return 'norepeat'

def _get_repeat_dates(self, x):
    if x[3].startswith('BY'):
        zone_time = x[4].split('+')[-1:][0].split(':')[0][:4]
    else:
        zone_time = x[3].split('+')[-1:][0].split(':')[0][:4]
    tz_format = zone_time[:2]+':'+zone_time[2:]
    repeat_start = x[1].split('\n')[0].split(':')[1]
    repeat_end = x[2].split('\n')[0].split(':')[1]
    o = repeat_start.split('T')
    repeat_start = str(o[0][:4]) + '-' + str(o[0][4:6]) + '-' + str(o[0][6:8])
    if len(o) == 2:
        repeat_start += ' ' + str(o[1][:2]) + ':' + str(o[1][2:4]) + ':' + str(o[1][4:6])
    else:
        repeat_start += ' ' + '00' + ':' + '00' + ':' + '00'
    p = repeat_end.split('T')
    repeat_end = str(p[0][:4]) + '-' + str(p[0][4:6]) + '-' + str(p[0][6:8])
    if len(p) == 2:
        repeat_end += ' ' + str(p[1][:2]) + ':' + str(p[1][2:4]) + ':' + str(p[1][4:6])
    else:
        repeat_end += ' ' + '00' + ':' + '00' + ':' + '00'
    return (repeat_start, repeat_end, tz_format)

def tformat_google(self, start_time, end_time):
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

    return (start_time, end_time)

def _get_tinydates(self, stime, etime):
    stime = dateutil.parser.parse(stime)
    etime = dateutil.parser.parse(etime)
    try:
        au_dt = au_tz.normalize(stime.astimezone(au_tz))
        timestring = datetime.datetime(*au_dt.timetuple()[:6]).strftime('%Y-%m-%d %H:%M:%S')
        au_dt = au_tz.normalize(etime.astimezone(au_tz))
        timestring_end = datetime.datetime(*au_dt.timetuple()[:6]).strftime('%Y-%m-%d %H:%M:%S')
    except:
        timestring = datetime.datetime(*stime.timetuple()[:6]).strftime('%Y-%m-%d %H:%M:%S')
        timestring_end = datetime.datetime(*etime.timetuple()[:6]).strftime('%Y-%m-%d %H:%M:%S')
    return (timestring, timestring_end)

class google_calendar_wizard(wizard.interface):

    calendar_service = ""

    def add_repeat_event(self, calender_service, title='', content='', where='', start_time=None, end_time=None, repeat_status='yearly', recurrence_data=None):
        try:
            start_time, end_time = tformat_google(self, start_time, end_time)
            ts = time.strptime(start_time[:19], "%Y-%m-%dT%H:%M:%S")
            start_time_google = time.strftime("%Y%m%dT%H%M%S", ts)
            ts1 = time.strptime(end_time[:19], "%Y-%m-%dT%H:%M:%S")
            end_time_google = time.strftime("%Y%m%dT%H%M%S", ts1)
            if recurrence_data is None:
                # to do: add timezone information + until attribute...
                if repeat_status == 'monthly':
                    recurrence_data = ('DTSTART;VALUE=DATE:%s\r\n'
                                         + 'DTEND;VALUE=DATE:%s\r\n'
                                         + 'RRULE:FREQ=MONTHLY;BYDAY=-1MO;\r\n')%(start_time_google, end_time_google) # -1MO == last monday of the month
                elif repeat_status in ['yearly', 'daily']:
                    if repeat_status == 'yearly':
                        rs = 'YEARLY'
                    elif repeat_status == 'daily':
                        rs = 'DAILY'
                    recurrence_data = ('DTSTART;VALUE=DATE:%s\r\n'
                                         + 'DTEND;VALUE=DATE:%s\r\n'
                                         + 'RRULE:FREQ=%s;\r\n')%(start_time_google, end_time_google, rs)
                else:
                    if repeat_status == 'weekly':
                        rs = 'MO' #Fix me (Monday)
                    elif repeat_status == 'everyweekday':
                        rs = 'MO,TU,WE,TH,FR'
                    elif repeat_status == 'every_m_w_f':
                        rs = 'MO,WE,FR'
                    elif repeat_status == 'every_t_t':
                        rs = 'TU,TH'
                    recurrence_data = ('DTSTART;VALUE=DATE:%s\r\n'
                                         + 'DTEND;VALUE=DATE:%s\r\n'
                                         + 'RRULE:FREQ=WEEKLY;BYDAY=%s;\r\n')%(start_time_google, end_time_google, rs)

            event = gdata.calendar.CalendarEventEntry()
            event.title = atom.Title(text=title)
            event.content = atom.Content(text=content)
            event.where.append(gdata.calendar.Where(value_string=where))
            # Set a recurring event
            event.recurrence = gdata.calendar.Recurrence(text=recurrence_data)
            event.batch_id = gdata.BatchId(text='insert-request')
            return event
#            new_event = calender_service.InsertEvent(event, '/calendar/feeds/default/private/full')
#            return new_event
        except Exception, e:
            raise osv.except_osv('Error !', e )

    def add_event(self, calendar_service, title='', content='', where='', start_time=None, end_time=None):
        try:
            event = gdata.calendar.CalendarEventEntry()
            event.title = atom.Title(text=title)
            event.content = atom.Content(text=content)
            event.where.append(gdata.calendar.Where(value_string=where))
            start_time, end_time = tformat_google(self, start_time, end_time)
            event.when.append(gdata.calendar.When(start_time=start_time, end_time=end_time))
            event.batch_id = gdata.BatchId(text='insert-request')
            return event
#            new_event = calendar_service.InsertEvent(event, '/calendar/feeds/default/private/full')
#            return new_event
        except Exception, e:
            raise osv.except_osv('Error !', e )

    def _synch_events(self, cr, uid, data, context={}):
#        To do import:
#            - Retrieving events for a specified date range
#            - delete events

#         To do export:
#            1. multiple location of events
#            2. delete events

        obj_user = pooler.get_pool(cr.dbname).get('res.users')
        product = pooler.get_pool(cr.dbname).get('product.product').search(cr, uid, [('name', 'like', 'Calendar Product')])
        google_auth_details = obj_user.browse(cr, uid, uid)
        obj_event = pooler.get_pool(cr.dbname).get('event.event')
        if not google_auth_details.google_email or not google_auth_details.google_password:
            raise osv.except_osv('Warning !', 'Please Enter google email id and password in users')
        if 'tz' in context and context['tz']:
            time_zone = context['tz']
        else:
            time_zone = data['form']['timezone_select']
        au_tz = timezone(time_zone)
#        try :
        self.calendar_service = gdata.calendar.service.CalendarService()
        self.calendar_service.email = google_auth_details.google_email
        self.calendar_service.password = google_auth_details.google_password
        self.calendar_service.source = 'Tiny Event'
        self.calendar_service.ProgrammaticLogin()
        tiny_events = obj_event.search(cr, uid, [])
        location = ''
        if google_auth_details.company_id.partner_id.address:
            add = google_auth_details.company_id.partner_id.address[0]
            city = add.city or ''
            street = add.street or ''
            street2 = add.street2 or ''
            zip = add.zip or ''
            country = add.country_id and add.country_id.name or ''
            location = street + " " +street2 + " " + city + " " + zip + " " + country
        tiny_events = obj_event.browse(cr, uid, tiny_events, context)
        feed = self.calendar_service.GetCalendarEventFeed()
        tiny_event_dict = {}
        summary_dict = {}
        keys = ['Event Created In Tiny', 'Event Modified In Tiny', 'Event Created In Google', 'Event Modified In Google', 'Error in Event While try to modify in Google']
        map(lambda key:summary_dict.setdefault(key, 0), keys)
        request_feed = gdata.calendar.CalendarEventFeed()
        event_ids = []
        for event in tiny_events:
            if not event.google_event_id:
                event_ids.append(event.id)
                summary_dict['Event Created In Google'] += 1
                if not event.repeat_status == 'norepeat':
                    new_event = self.add_repeat_event(self.calendar_service, event.name, event.name, location, event.date_begin, event.date_end, event.repeat_status, None)
                    request_feed.AddInsert(entry=new_event)
                else:
                    new_event = self.add_event(self.calendar_service, event.name, event.name, location, event.date_begin, event.date_end)
                    request_feed.AddInsert(entry=new_event)
                tiny_event_dict[event.google_event_id] = event
            tiny_event_dict[event.google_event_id] = event
        if event_ids:
            response_feed = self.calendar_service.ExecuteBatch(request_feed, gdata.calendar.service.DEFAULT_BATCH_URL)
            for entry in response_feed.entry:
                obj_event.write(cr, uid, event_ids, {'google_event_id': entry.id.text, 'event_modify_date': entry.updated.text })

        request_up_feed = gdata.calendar.CalendarEventFeed()
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
                    if an_event and not an_event.when:# Fix me
                        # recurrence value should be modified here to fix
                        summary_dict['Error in Event While try to modify in Google'] += 1
                    else:
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
                        an_event.batch_id = gdata.BatchId(text='update-request')
                        request_up_feed.AddUpdate(entry=an_event)
#                        update_event = self.calendar_service.UpdateEvent(an_event.GetEditLink().href, an_event)
                        summary_dict['Event Modified In Google'] += 1
                elif event.write_date < google_up:
                    # google events => tiny
                    utime = dateutil.parser.parse(an_event.updated.text)
                    au_dt = au_tz.normalize(utime.astimezone(au_tz))
                    timestring_update = datetime.datetime(*au_dt.timetuple()[:6]).strftime('%Y-%m-%d %H:%M:%S')
                    name_event = an_event.title.text or ''
                    if an_event and not an_event.when:
#                            summary_dict['Error in Event While try to modify in Tiny'] += 1
                        x = an_event.recurrence.text.split(';')
                        status = x[2].split('=')[-1:] and x[2].split('=')[-1:][0] or ''
                        status_day = x[3].split('=')
                        byday = ''
                        if status_day and status_day[0] == 'BYDAY':
                            byday = status_day[1]

                        repeat_status = _get_repeat_status(self, status, byday)
                        repeat_start, repeat_end, zone_time = _get_repeat_dates(self, x)
#                        parse_start =  parse(str(repeat_start)+ '+' + zone_time)
#                        parse_end =  parse(str(repeat_end)+ '+' + zone_time)
#                        repeat_start = dateutil.parser.parse(parse_start.isoformat())
#                        repeat_end = dateutil.parser.parse(parse_end.isoformat())
#                        try:
#                            au_dt = au_tz.normalize(repeat_start.astimezone(au_tz))
#                            timestring = datetime.datetime(*au_dt.timetuple()[:6]).strftime('%Y-%m-%d %H:%M:%S')
#                            au_dt = au_tz.normalize(repeat_end.astimezone(au_tz))
#                            timestring_end = datetime.datetime(*au_dt.timetuple()[:6]).strftime('%Y-%m-%d %H:%M:%S')
#                        except :
#                            timestring = datetime.datetime(*repeat_start.timetuple()[:6]).strftime('%Y-%m-%d %H:%M:%S')
#                            timestring_end = datetime.datetime(*repeat_end.timetuple()[:6]).strftime('%Y-%m-%d %H:%M:%S')
                        timestring = time.strftime('%Y-%m-%d %H:%M:%S', time.strptime(repeat_start, "%Y-%m-%d %H:%M:%S"))
                        timestring_end = time.strftime('%Y-%m-%d %H:%M:%S', time.strptime(repeat_end, "%Y-%m-%d %H:%M:%S"))
                    else:
                        repeat_status = 'norepeat'
                        stime = an_event.when[0].start_time
                        etime = an_event.when[0].end_time
                        timestring, timestring_end = _get_tinydates(self, an_event.when[0].start_time, an_event.when[0].end_time)
                    val = {
                       'name': name_event,
                       'date_begin': timestring,
                       'date_end': timestring_end,
                       'event_modify_date': timestring_update,
                       'repeat_status': repeat_status or 'norepeat',
                       'privacy': _get_privacy(self, an_event.visibility.value),
                       'email': ', '.join(map(lambda x: x.name, an_event.who))
                       }
                    obj_event.write(cr, uid, [event.id], val)
                    summary_dict['Event Modified In Tiny'] += 1

                elif event.write_date == google_up:
                    pass
            else:
                google_id = an_event.id.text
                utime = dateutil.parser.parse(an_event.updated.text)
                au_dt = au_tz.normalize(utime.astimezone(au_tz))
                timestring_update = datetime.datetime(*au_dt.timetuple()[:6]).strftime('%Y-%m-%d %H:%M:%S')
                name_event = an_event.title.text or ''
                if an_event and not an_event.when:
#                        summary_dict['Error in Event While try to create in Tiny'] += 1
                    x = an_event.recurrence.text.split(';')
                    status = x[2].split('=')[-1:] and x[2].split('=')[-1:][0] or ''
                    status_day = x[3].split('=')
                    byday = ''
                    if status_day and status_day[0] == 'BYDAY':
                        byday = status_day[1]

                    repeat_status = _get_repeat_status(self, status, byday)
                    repeat_start, repeat_end, zone_time = _get_repeat_dates(self, x)
#                    parse_start =  parse(str(repeat_start)+ '+' + zone_time)
#                    parse_end =  parse(str(repeat_end)+ '+' + zone_time)
#                    repeat_start = dateutil.parser.parse(parse_start.isoformat())
#                    repeat_end = dateutil.parser.parse(parse_end.isoformat())
#                    try:
#                        au_dt = au_tz.normalize(repeat_start.astimezone(au_tz))
#                        timestring = datetime.datetime(*au_dt.timetuple()[:6]).strftime('%Y-%m-%d %H:%M:%S')
#                        au_dt = au_tz.normalize(repeat_end.astimezone(au_tz))
#                        timestring_end = datetime.datetime(*au_dt.timetuple()[:6]).strftime('%Y-%m-%d %H:%M:%S')
#                    except:
#                        timestring = datetime.datetime(*repeat_start.timetuple()[:6]).strftime('%Y-%m-%d %H:%M:%S')
#                        timestring_end = datetime.datetime(*repeat_end.timetuple()[:6]).strftime('%Y-%m-%d %H:%M:%S')
                    timestring = time.strftime('%Y-%m-%d %H:%M:%S', time.strptime(repeat_start, "%Y-%m-%d %H:%M:%S"))
                    timestring_end = time.strftime('%Y-%m-%d %H:%M:%S', time.strptime(repeat_end, "%Y-%m-%d %H:%M:%S"))
                else:
                    repeat_status = 'norepeat'
                    timestring, timestring_end = _get_tinydates(self, an_event.when[0].start_time, an_event.when[0].end_time)
                val = {
                   'name': name_event,
                   'date_begin': timestring,
                   'date_end': timestring_end,
                   'product_id': product and product[0] or 1,
                   'google_event_id': an_event.id.text,
                   'event_modify_date': timestring_update,
                   'repeat_status': repeat_status or 'norepeat',
                   'privacy': _get_privacy(self, an_event.visibility.value),
                   'email': ', '.join(map(lambda x: x.name, an_event.who))
                    }
                obj_event.create(cr, uid, val)
                summary_dict['Event Created In Tiny'] += 1

        response_up_feed = self.calendar_service.ExecuteBatch(request_up_feed, gdata.calendar.service.DEFAULT_BATCH_URL)
        final_summary = '************Summary************ \n'
        for sum in summary_dict:
            final_summary += '\n' + str(sum) + ' : ' + str(summary_dict[sum]) + '\n'
        final_summary += '\n\nNote: Currently repeated events can not be modified in google, Its work with un-repeated events(Does not repeat)'
        return {'summary': final_summary}
#        except Exception, e:
#            raise osv.except_osv('Erroraa !', e )

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
            'result': {'type': 'form', 'arch': _summary_form, 'fields': _summary_fields, 'state': [('end', 'Ok')]}
        }
    }

google_calendar_wizard('google.calendar.synch')

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: