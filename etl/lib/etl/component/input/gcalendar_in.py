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

class gcalendar_in(component):

    def __init__(self, gcalendar_conn, name='component.input.gmail_in', transformer=None, row_limit=0):
        """
        Required  Parameters
        gcalendar_conn     : connector for google calendar

        Extra Parameters
        name          : Name of Component.
        row_limit     : Limited records are sent to destination if row limit is specified. If row limit is 0, all records are sent.
        """
        super(gcalendar_in, self).__init__(connector=gcalendar_conn, name=name, transformer=transformer, row_limit=row_limit)
        self._type = 'component.input.gcalendar_in'

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
        feed = self.connector.GetCalendarEventFeed()
        rows = []
        data = {}
        for i, an_event in enumerate(feed.entry):
            print i,an_event
            yield {}, 'main'

def test():
    from etl_test import etl_test
    import etl
    import getpass
    user = raw_input('Enter gmail username: ')
    user = user + '@gmail.com'
    password = getpass.unix_getpass("Enter your password:")
    cal_conn=etl.connector.gcalendar_connector(user, password)
    cal_service = cal_conn.open()
    print cal_service
    in_calendar = gcalendar_in(cal_service)

    test = etl_test.etl_component_test(in_calendar)
#    test.check_output([{'phone_numbers': [''], 'postal_addresses': [''], 'emails': [''], 'title': ''}], 'main')
    # here add the details of the contact in your gmail in the above mentioned format
    res = test.output()
    print "hooo"

if __name__ == '__main__':
    test()
