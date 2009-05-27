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
from etl.component.input import xmlrpc_in

class xmlrpc_in_block(xmlrpc_in):
    """
    To connect server with xmlrpc request.

    """
    _register_functions=[]

    def __init__(self, xmlrpc_connector, job, name='component.input.xmlrpc_in_block', transformer=None, row_limit=0):        
        super(xmlrpc_in_block, self).__init__(xmlrpc_connector, job, name=name, transformer=transformer, row_limit=row_limit)
        self._type = 'component.input.xmlrpc_in_block'    


    

    def process(self):
        start_com = False
        end_com = False
        start_dummy = etl.component.component(name='start dummy')
        end_dummy = etl.component.component(name='end dummy')
        for com in self.rel_job.get_components():
            if com.is_start():
                start_com = com
            if com.is_end():
                end_com = com
        self.rel_job.add_component(start_dummy)
        self.rel_job.add_component(end_dummy)
        if start_com:
            tran = etl.transition(start_dummy,start_com)
        if end_com:
            tran = etl.transition(end_com,end_dummy)
        self.start_dummy = start_dummy
        self.end_dummy = end_dummy
        self.end_dummy.datas = []
        self.connector.start(self.import_data)        
        for d in self.datas:
            yield d, 'main'

    def iterator(self, datas=[]):
        for d in datas:
            yield d, 'main'

    def end_iterator(self):                
        self.end_dummy.datas = []
        for channel, trans in self.end_dummy.input_get().items():
            for iterator in trans:
                for d in iterator:
                    self.end_dummy.datas.append(d)        
        for d in self.end_dummy.datas:
            yield d, 'main'


    def import_data(self, datas):
        self.datas = datas
        for com in self.rel_job.get_components():
            com.generator = False
        self.start_dummy.generator = self.iterator(self.datas)
        self.end_dummy.generator = self.end_iterator()
        self.rel_job.run()
        return self.end_dummy.datas

def test():
    pass

if __name__ == '__main__':
    test()
