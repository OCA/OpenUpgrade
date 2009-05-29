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
To provide connectivity with Facebook

Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>).
GNU General Public License
"""
import datetime
import time
from etl.connector import connector

class gcalendar_connector(connector):
    """
    This is an ETL connector that is used to provide connectivity with google calendar server.
    """
    def __init__(self, email, password, delay_time=20, name='calendar_connector'):
        """
        Required Parameters
        email : Google email.
        password        : password for gmail user

        Extra Parameters
        delay_time  : Time in sec which is use to wait for login while opening login page in browser.
        name        : Name of connector.
        """
        super(gcalendar_connector, self).__init__(name)
        self._type = 'connector.calendar_connector'
        self.email = email
        self.password = password
        self.delay_time = delay_time
        self.calendar_service = False

    def open(self):
        """
        Opens connection to google calendar.
        """
        from gdata import service
        import gdata.calendar.service
        import gdata.calendar
        import atom

        super(gcalendar_connector, self).open()
        self.calendar_service = gdata.calendar.service.CalendarService()
        self.calendar_service.email = self.email
        self.calendar_service.password = self.password
        self.calendar_service.source = 'Tiny'
        self.calendar_service.max_results = 500 # to be check
        self.calendar_service.ProgrammaticLogin()
        return self.calendar_service

    def execute(self, facebook, method, fields):
        """
        Required Parameters
            To do: descrption
        """
        rows = {}
        return rows

    def __getstate__(self):
        res = super(gcalendar_connector, self).__getstate__()
        res.update({'email':self.email, 'password':self.password, 'delay_time':self.delay_time, 'calendar_service':self.calendar_service})
        return res

    def __setstate__(self, state):
        super(gcalendar_connector, self).__setstate__(state)
        state['_signal__connects'] = {}
        self.__dict__ = state

    def __copy__(self):
        """
        Overrides copy method.
        """
        res = gcalendar_connector(self.email, self.password, self.delay_time, self.name)

        return res


def test():
    """
    Test function.
    """
    from etl_test import etl_test
    import etl
    cal_conn=gcalendar_connector('username','password')
    cal_service = cal_conn.open()
    print cal_service

if __name__ == '__main__':
    test()

