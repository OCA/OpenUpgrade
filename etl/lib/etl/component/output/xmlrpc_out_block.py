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
 To get the response for the request made to xmlrpc server.

 Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>).
 GNU General Public License.
"""

from etl.component.output import xmlrpc_out

class xmlrpc_out_block(xmlrpc_out):
    """
    To get the response for the request made to xmlrpc server.
    """
    def __init__(self, xmlrpc_connector, name='component.output.xmlrpc_out_block', transformer=None, row_limit=0):
        super(xmlrpc_out_block, self).__init__(xmlrpc_connector, name=name, transformer=transformer, row_limit=row_limit)
        self._type = 'component.output.xmlrpc_out_block'

    

    def process(self):
        self.server = False
        datas = []
        for channel, trans in self.input_get().items():
            for iterator in trans:
                for d in iterator:
                    self.server = self.connector.connect()                    
                    datas = self.server.import_data([d])                    
                    self.connector.close(self.server)
                    self.server = False
                    for d in datas:                                       
                        yield d, channel

def test():
    pass

if __name__ == '__main__':
    test()


