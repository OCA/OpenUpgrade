# -*- encoding: utf-8 -*-
##############################################################################
#
#    ETL system- Extract Transfer Load system
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
"""
This is an ETL Component that writes data to google calendar.
"""

from etl.component import component
from etl.connector import openobject_connector
import time
import datetime
import dateutil
from dateutil.tz import *
from dateutil.parser import *
from pytz import timezone
import pytz



class gcalendar_out(component):
    """
    This is an ETL Component that writes data to google calendar.
    """

    def __init__(self, gcalendar_conn, name='component.output.gcalendar_out', transformer=None, row_limit=0):
        super(gcalendar_out, self).__init__(name=name, connector=gcalendar_conn, transformer=transformer, row_limit=row_limit)
        self._type = 'component.output.gcalendar_out'

    def __copy__(self):
        res = gcalendar_out(self.connector, self.name, self.transformer, self.row_limit)
        return res

    def end(self):
        super(gcalendar_out, self).end()

    def __getstate__(self):
        res = super(gcalendar_out, self).__getstate__()
        return res

    def __setstate__(self, state):
        super(gcalendar_out, self).__setstate__(state)
        self.__dict__ = state

    def process(self):
        import gdata.contacts.service
        import atom
        from etl_test import etl_test
        import etl
        calendar_service = self.connector.open()
        event = gdata.calendar.CalendarEventEntry()

        ooconnector=openobject_connector('http://localhost:8069', 'test', 'admin', 'admin',con_type='xmlrpc')
        oo_in_event = etl_test.etl_component_test(etl.component.input.openobject_in(
                         ooconnector,'event.event',
                         fields=['name', 'date_begin', 'date_end'],
        ))
        res = oo_in_event.output()

        for d in res['main']:
            event.title = atom.Title(text=d['name'])
            event.content = atom.Content(text=d['name'])

            time_format = "%Y-%m-%d %H:%M:%S"
            start_time = d['date_begin']
            timestring = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(time.mktime(time.strptime(start_time, "%Y-%m-%d %H:%M:%S"))))
            starttime = time.strptime(timestring, time_format)
            start_time = time.strftime('%Y-%m-%dT%H:%M:%S.000Z', starttime)

            end_time = d['date_end']
            timestring_end = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(time.mktime(time.strptime(end_time, "%Y-%m-%d %H:%M:%S"))))
            endtime = time.strptime(timestring_end, time_format)
            end_time = time.strftime('%Y-%m-%dT%H:%M:%S.000Z', endtime)

            if start_time is None:
                  start_time = time.strftime('%Y-%m-%dT%H:%M:%S.000Z', time.gmtime())
                  end_time = time.strftime('%Y-%m-%dT%H:%M:%S.000Z', time.gmtime(time.time() + 3600))

            event.when = []
            event.when.append(gdata.calendar.When(start_time=start_time, end_time=end_time))
            new_event = calendar_service.InsertEvent(event, "/calendar/feeds/default/private/full")

            yield new_event, 'main'

def test():
    from etl_test import etl_test
    import etl
    import getpass
    user = raw_input('Enter gmail username: ')
    user = user + '@gmail.com'
    password = getpass.unix_getpass("Enter your password:")
    cal_conn=etl.connector.gcalendar_connector(user, password)

    out_calendar = gcalendar_out(cal_conn)

    test = etl_test.etl_component_test(out_calendar)

#    ooconnector=openobject_connector('http://localhost:8069', 'test', 'admin', 'admin',con_type='xmlrpc')
#    oo_in_event = etl_test.etl_component_test(etl.component.input.openobject_in(
#                     ooconnector,'event.event',
#                     fields=['name', 'date_begin', 'date_end'],
#    ))

    res = test.output()


if __name__ == '__main__':
    test()
