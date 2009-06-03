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
To provide connectivity with blogger

Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>).
GNU General Public License
"""
from etl.connector import connector

class gblog_connector(connector):
    """
    This is an ETL connector that is used to provide connectivity with blog server.
    """
    def __init__(self, email, password, delay_time=20, name='gblog_connector'):
        """
        Required Parameters
        email : blogger email.
        password        : password for blogger user

        Extra Parameters
        delay_time  : Time in sec which is use to wait for login while opening login page in browser.
        name        : Name of connector.
        """
        super(gblog_connector, self).__init__(name)
        self._type = 'connector.gblog_connector'
        self.email = email
        self.password = password
        self.delay_time = delay_time
        self.gblog_service = False

    def open(self):
        """
        Opens connection to blogger.
        """
        from gdata import service

        super(gblog_connector, self).open()
        self.gblog_service = service.GDataService(self.email, self.password)
        self.gblog_service.source = 'Tiny'
        self.gblog_service.service = 'blogger'
        self.gblog_service.server = 'www.blogger.com'
        self.gblog_service.ProgrammaticLogin()
        return self.gblog_service

    def execute(self, facebook, method, fields):
        """
        Required Parameters
            To do: descrption
        """
        rows = {}
        return rows

    def __getstate__(self):
        res = super(gblog_connector, self).__getstate__()
        res.update({'email':self.email, 'password':self.password, 'delay_time':self.delay_time, 'gblog_service':self.gblog_service})
        return res

    def __setstate__(self, state):
        super(gblog_connector, self).__setstate__(state)
        self.__dict__ = state

    def __copy__(self):
        """
        Overrides copy method.
        """
        res = gblog_connector(self.email, self.password, self.delay_time, self.name)
        return res

def test():
    from etl_test import etl_test
    import etl
    import getpass

    user = raw_input('Enter blogger username: ')
    password = getpass.unix_getpass("Enter your password:")
    gblog_conn = gblog_connector(user, password)
    gblog_service = gblog_conn.open()
    print gblog_service

if __name__ == '__main__':
    test()
