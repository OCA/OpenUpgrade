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
 to run xmlrpc server

 Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>).
 GNU General Public License
"""
from etl.component import component

#
class xmlrpc_in(component):
    """
    To connect server with xmlrpc request

    """
    _register_functions=[]

    def __init__(self, xmlrpc_connector,  name='component.input.xmlrpc_in', transformer=None, row_limit=0):
        """
        To be update
        """
        super(xmlrpc_in, self).__init__(name=name,connector=xmlrpc_connector, transformer=transformer, row_limit=0)
        self._type='component.input.xmlrpc_in'        
        self.datas=[]
        self.isStarted=False
        self.register_functions(self.import_data)

    def __copy__(self):        
        res=xmlrpc_in(self.xmlrpc_connector, self.name, self.transformer, self.row_limit)
        return res

    def register_functions(self,fun):
        self._register_functions.append(fun)

    def process(self):
        from SimpleXMLRPCServer import SimpleXMLRPCServer
        from SimpleXMLRPCServer import SimpleXMLRPCRequestHandler
        import threading
        self.connector.start(self.import_data)
        for d in self.datas:
            yield d,'main'

    def iterator(self,datas=[]):
        if self.transformer:
            row=self.transformer.transform(self.datas)
        for d in datas:
            yield d, 'main'

    def data_iterator(self,datas):
        pass

    def import_data(self, datas):
        self.generator=self.data_iterator(datas)
        return True

def test():
    pass
if __name__ == '__main__':
#    test()
    pass
