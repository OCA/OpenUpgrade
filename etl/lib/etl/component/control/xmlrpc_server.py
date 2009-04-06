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
from SimpleXMLRPCServer import SimpleXMLRPCServer
from SimpleXMLRPCServer import SimpleXMLRPCRequestHandler

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
        self.server = False

    def process(self):
        server = SimpleXMLRPCServer((self.host, self.port))
        server.register_introspection_functions()
        server.register_function(self.import_data)
        server.register_function(self.export_data)
        server.serve_forever()
        self.server = server
        return True

    def import_data(self, data):#to be check
        if data:
            self.job.action_start(key, signal_data=data, data={})
        else:
            self.job.action_pause(key, signal_data={}, data={})

    def export_data(self, data):
        pass

def test():
    pass
if __name__ == '__main__':
#    test()
    pass
