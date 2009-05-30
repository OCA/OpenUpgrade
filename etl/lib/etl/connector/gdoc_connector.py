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
To provide connectivity with Google doc

Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>).
GNU General Public License
"""
from etl.connector import connector

class gdoc_connector(connector):
    """
    This is an ETL connector that is used to provide connectivity with google doc server.
    """
    def __init__(self, email, password, delay_time=20, name='gdoc_connector'):
        """
        Required Parameters
        email : Google email.
        password        : password for gmail user

        Extra Parameters
        delay_time  : Time in sec which is use to wait for login while opening login page in browser.
        name        : Name of connector.
        """
        super(gdoc_connector, self).__init__(name)
        self._type = 'connector.gdoc_connector'
        self.email = email
        self.password = password
        self.delay_time = delay_time
        self.gdoc_service = False

    def open(self):
        """
        Opens connection to google doc.
        """
        import gdata.docs.service

        super(gdoc_connector, self).open()
        # Create a client class which will make HTTP requests with Google Docs server.
        self.gdoc_service = gdata.docs.service.DocsService()
        self.gdoc_service.ClientLogin(self.email, self.password)
        return self.gdoc_service

    def execute(self, facebook, method, fields):
        """
        Required Parameters
            To do: descrption
        """
        rows = {}
        return rows

    def __getstate__(self):
        res = super(gdoc_connector, self).__getstate__()
        res.update({'email':self.email, 'password':self.password, 'delay_time':self.delay_time, 'gdoc_service':self.gdoc_service})
        return res

    def __setstate__(self, state):
        super(gdoc_connector, self).__setstate__(state)
        self.__dict__ = state

    def __copy__(self):
        """
        Overrides copy method.
        """
        res = gdoc_connector(self.email, self.password, self.delay_time, self.name)
        return res

def test():
    """
    Test function.
    """
    from etl_test import etl_test
    import etl
    import getpass
    user = raw_input('Enter gmail username: ')
    password = getpass.unix_getpass("Enter your password:")
    gdoc_conn = gdoc_connector(user, password)
    gdoc_service = gdoc_conn.open()
    documents_feed = gdoc_service.GetDocumentListFeed()
    for document_entry in documents_feed.entry:
        # Display the title of the document on the command line.
        print document_entry.title.text
    print gdoc_service

if __name__ == '__main__':
    test()
