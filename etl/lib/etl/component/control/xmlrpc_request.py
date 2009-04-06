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
 to connect server with xmlrpc request

 Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>).
 GNU General Public License
"""
from etl.component import component

class xmlrpc_request(component):
    """
    To connect server with xmlrpc request

    """

    def __init__(self, job, host='localhost', port=5000, uid='admin', password='admin',name='xmlrpc', transformer=None):
        """
        To be update
        """
        super(xmlrpc_request, self).__init__(name, transformer=transformer)
        self.job = job
        self.host=host
        self.port=port
        self.uid=uid
        self.password=password

    def process(self):
        import xmlrpclib
        server = xmlrpclib.ServerProxy('http://localhost:8069/xmlrpc/object')
        login1 = xmlrpclib.ServerProxy(self.host+'/xmlrpc/common')
        login1.login('etl', 'admin','admin')
        res = getattr(server,'get_data')('etl','admin','admin', *args) # get data!!!
        if res:
            self.job.action_start(key,signal_data={},data={})
        else:
            self.job.action_pause(key,signal_data={},data={})
        print server
        return True

def test():
    from etl_test import etl_test
    import etl
#    facebook_conn=etl.connector.facebook_connector('http://facebook.com', 'modiinfo@gmail.com')
    test1=etl_test.etl_component_test(xmlrpc_request('job','localhost', 5000))
    res=test1.output()

if __name__ == '__main__':
    test()
