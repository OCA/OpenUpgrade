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

    def __init__(self,openobject_connector,model,fields=None,name='component.output.openobject_out',transformer=None):
        """ 
        Parameters ::
        openobject_connector : openobject connector to connect with openerp server
        transformer          : transformer object to transform string data into particular object.
        fields               : a fields of openobject model.
        model                : a openobject model name.
        """    
        super(openobject_out, self).__init__(name,transformer=transformer)
        self.fields = fields
        self.openobject_connector = openobject_connector
        self.model=model

    def process(self):        
        datas = []
        self.fields_keys = None
        for channel,trans in self.input_get().items():
            for iterator in trans:
                for d in iterator:
                    if not self.fields:
                        self.fields = dict(map(lambda x: (x,x), d.keys()))
                    if type(self.fields)==type([]):
                        self.fields_keys = self.fields
                        self.fields = dict(map(lambda x: (x,x), self.fields))
                    if not self.fields_keys:
                        self.fields_keys = self.fields.keys()
                    try:
                        if self.transformer:
                            d=self.transformer.transform(d)
                        print d
                        connector=self.openobject_connector.open()
                        self.openobject_connector.execute(connector,'execute', self.model, 'import_data', self.fields_keys, [map(lambda x: d[self.fields[x]], self.fields_keys)])
                        self.openobject_connector.close(connector)
                        yield d, 'main'
                    except Exception,e:
                        print 'error',e
                        yield {'data':d,'type':'exception','message':str(e)}, 'error'


def test():
    from etl_test import etl_test
    import etl
    openobject_conn=etl.connector.openobject_connector('http://localhost:8069', 'trunk', 'admin', 'admin',con_type='xmlrpc')
    test=etl_test.etl_component_test(openobject_out('test',openobject_conn,'res.partner'))
    test.check_input({'main':[{'name':'OpenERP1'},{'name':'Fabien1'}]})
    test.check_output([{'name':'OpenERP1'},{'name':'Fabien1'}],'main')
    res=test.output()

if __name__ == '__main__':
    test()
