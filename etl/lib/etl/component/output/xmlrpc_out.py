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
To do: comment
"""

from etl.component import component

class xmlrpc_out(component):
    """
    # To do: comment
    """
    def __init__(self, xmlrpc_connector, method=None,datas=[], name='component.output.xmlrpc_out', transformer=None):
        super(xmlrpc_out, self).__init__(name, transformer=transformer)
        self.xmlrpc_connector = xmlrpc_connector
        self.method = method
        self.datas=datas

    def process(self):
        server=False
        for channel,trans in self.input_get().items():
            for iterator in trans:
                for d in iterator:
                    if not server:
                        server = self.xmlrpc_connector.connect()
                    server.import_data([d])
                    yield d, 'main'

def test():
    pass

if __name__ == '__main__':
    pass

#s = xmlrpclib.ServerProxy('http://localhost:5000')
#s.import_data([
#    {'org':'X.Ltd','fn':'Mr.X','email':'x@xmail.com'},
#    {'org':'Y.Ltd','fn':'Mr.Y','email':'y@ymail.com'},
#    {'org':'X.Ltd','fn':'Mr.XX','email':'xx@xmail.com'},
#    {'org':'X.Ltd','fn':'Mr.X2','email':'x2@xmail.com'},
#    {'org':'Y.Ltd','fn':'Mr.Y1','email':'y1@ymail.com'},
#    ])
