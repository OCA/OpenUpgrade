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

from etl.component import component
import datetime
import dateutil
import time
from dateutil.parser import *

class gcalendar_in(component):

    def __init__(self, gcalendar_conn, datetime_format='%Y-%m-%d %H:%M:%S', timezone='Asia/Calcutta', name='component.input.gcalendar_in', transformer=None, row_limit=0):
        """
        Required  Parameters
        gcalendar_conn     : connector for google calendar

        Extra Parameters
        name          : Name of Component.
        row_limit     : Limited records are sent to destination if row limit is specified. If row limit is 0, all records are sent.
        """
        super(gcalendar_in, self).__init__(connector=gcalendar_conn, name=name, transformer=transformer, row_limit=row_limit)
        self._type = 'component.input.gcalendar_in'
        self.datetime_format = datetime_format
        self.timezone = timezone

    def __copy__(self):
        res = gcalendar_in(self.gcalendar_conn, self.name, self.transformer, self.row_limit)
        return res

    def __getstate__(self):
        res = super(gcalendar_in, self).__getstate__()
        return res

    def __setstate__(self, state):
        super(gcalendar_in, self).__setstate__(state)
        self.__dict__ = state


    def process(self):
        import gdata.contacts.service
        calendar_service = self.connector.open()
        feed = calendar_service.GetCalendarEventFeed()
        for i, an_event in enumerate(feed.entry):
            data = {}
            data['name']= an_event.title.text
            for i in an_event.when:
                start_time = dateutil.parser.parse(i.start_time)
                end_time = dateutil.parser.parse(i.end_time)
                from pytz import timezone
                au_tz = timezone(self.timezone)
                au_dt = au_tz.normalize(start_time.astimezone(au_tz))
                timestring = datetime.datetime(*au_dt.timetuple()[:6]).strftime(self.datetime_format)
                au_dt = au_tz.normalize(end_time.astimezone(au_tz))
                timestring_end = datetime.datetime(*au_dt.timetuple()[:6]).strftime(self.datetime_format)
                data['date_begin'] = timestring
                data['date_end'] = timestring_end
            yield data, 'main'

def test():
    from etl_test import etl_test
    import etl
    from etl import transformer
    import getpass
    user = raw_input('Enter gmail username: ')
    user = user + '@gmail.com'
    password = getpass.unix_getpass("Enter your password:")
    cal_conn=etl.connector.gcalendar_connector(user, password)
    in_calendar = gcalendar_in(cal_conn)

    test = etl_test.etl_component_test(in_calendar)

#    transformer_description= {'date_begin':transformer.DATETIME, 'date_end':transformer.DATETIME}
#    transformer=transformer(transformer_description)

#    test.check_output([{'date_end': '2009-05-23 15:00:00', 'date_begin': '2009-05-23 14:00:00', 'name': 'Outing'}, {'date_end': '2009-05-23 10:00:00', 'date_begin': '2009-05-23 09:00:00', 'name': 'Reporting'}, {'date_end': '2009-06-07 00:00:00', 'date_begin': '2009-06-06 00:00:00', 'name': 'Submission'}], 'main')
    # here add the details of the contact in your gmail in the above mentioned format
#    test1 = gcalender_in_component=etl_test.etl_component_test(etl.component.input.gcalendar_in(cal_conn,transformer=transformer))
    res = test.output()

if __name__ == '__main__':
    test()
