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
 To run xmlrpc server.

 Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>).
 GNU General Public License.
"""
import etl
from etl.component import component

class xmlrpc_in(component):
    """
    To connect server with xmlrpc request.

    """
    _register_functions=[]

    def __init__(self, xmlrpc_connector, job, name='component.input.xmlrpc_in', transformer=None, row_limit=0):
        """
        To be update
        """
        super(xmlrpc_in, self).__init__(name=name, connector=xmlrpc_connector, transformer=transformer, row_limit=row_limit)
        self._type = 'component.input.xmlrpc_in'
        self.datas = []
        self.rel_job = job
        
        self.register_functions(self.import_data)
        

    def __copy__(self):
        res = xmlrpc_in(self.connector, self.job, self.name, self.transformer, self.row_limit)
        return res

    def register_functions(self, fun):
        self._register_functions.append(fun)

    def process(self): 
        start_com = False
        dummy = etl.component.component(name='dummy')
        for com in self.rel_job.get_components():
            if com.is_start():
                start_com = com
        self.rel_job.add_component(dummy)        
        if start_com:
            tran = etl.transition(dummy,start_com)               
        self.dummy = dummy
        self.connector.start(self.import_data)        
        for d in self.datas:
            yield d, 'main'

    def iterator(self, datas=[]):                
        for d in datas:
            yield d, 'main'
    

    def import_data(self, datas): 
        self.datas = datas 
        for com in self.rel_job.get_components():
            com.generator = False   
        self.dummy.generator = self.iterator(self.datas)           
        self.rel_job.run()        
        return True

def test():
    from etl_test import etl_test
    import etl
    xmlrpc_conn=etl.connector.xmlrpc_connector('localhost', 8050)
    conn = xmlrpc_conn.start('import_data')
    test1 = etl_test.etl_component_test(xmlrpc_in(xmlrpc_conn))
    res = test1.output()
    print res

if __name__ == '__main__':
    test()
