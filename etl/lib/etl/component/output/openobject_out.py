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
To write data into openobject model.

Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>).
GNU General Public License
"""
from etl.component import component

class openobject_out(component):
    """
    This is an ETL Component that use to write data into sql table.

    Type: Data Component
    Computing Performance: Streamline
    Fields : a mapping {OpenObject Field Name : Flow Name}
    Input Flows: 0-x
    * .* : the main data flow with input data
    Output Flows: 0-1
    * main : return all data
    """

    def __init__(self, openobject_connector, model, fields=None, name='component.output.openobject_out', transformer=None, row_limit=0):
        """
        Paramters :-
        openobject_connector : Openobject connector to connect with openerp server
        model                : Openobject model name.    
                
        Extra Parameters ::
        name                : Name of Component.
        transformer          : Transformer object to transform string data into particular object.
        fields               : Fields of openobject model.
        model                : Openobject model name.        
        """    
        super(openobject_out, self).__init__(name=name, connector=openobject_connector, transformer=transformer, row_limit=row_limit)
        self._type='component.output.openobject_out'
        self.fields = fields        
        self.model=model

    def __copy__(self):        
        res=openobject_out(self.connector, self.model, self.fields, self.name, self.transformer, self.row_limit)
        return res
        
    def end(self):
        super(openobject_out, self).end()
        if self.op_oc:
            self.connector.close(self.op_oc)
            self.op_oc=False

    def process(self):       
        datas = []
        self.fields_keys = None
        self.op_oc=False
        for channel, trans in self.input_get().items():
            for iterator in trans:                
                for d in iterator:                    
                    if not self.fields:
                        self.fields = dict(map(lambda x: (x, x), d.keys()))
                    if type(self.fields)==type([]):
                        self.fields_keys = self.fields
                        self.fields = dict(map(lambda x: (x, x), self.fields))
                    if not self.fields_keys:
                        self.fields_keys = self.fields.keys()
                    
                    if not self.op_oc:                         
                        self.op_oc=self.connector.open()                        
                    self.connector.execute(self.op_oc, 'execute', self.model, 'import_data', self.fields_keys, [map(lambda x: d[self.fields[x]], self.fields_keys)])                                            
                    yield d, 'main'     
                    
    
    

def test():
    from etl_test import etl_test
    import etl
    openobject_conn=etl.connector.openobject_connector('http://localhost:8069', 'trunk', 'admin', 'admin', con_type='xmlrpc')
    test=etl_test.etl_component_test(openobject_out('test', openobject_conn, 'res.partner'))
    test.check_input({'main':[{'name':'OpenERP1'}, {'name':'Fabien1'}]})
    test.check_output([{'name':'OpenERP1'}, {'name':'Fabien1'}], 'main')
    res=test.output()

if __name__ == '__main__':
    test()
