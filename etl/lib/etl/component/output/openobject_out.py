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
 openobject_out

* Use to write data into openobject model.

: Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>). All Rights Reserved
: GNU General Public License
"""

from etl.component import component
import datetime

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
	Paramters ::

	openobject_connector : Provides  openobject connector to connect with file
	transformer          : Provides transformer object to transform string data into particular object.
	fields               : TODO
	model                : It is used to provide a openobject model name.

	"""
	
        super(openobject_out, self).__init__(name,transformer=transformer)
        self.fields = fields
        self.openobject_connector = openobject_connector
        self.model=model
        self.connector=False

    def action_start(self,key,singal_data={},data={}):
        res = super(openobject_out, self).action_start(key,singal_data,data)
        self.connector=self.openobject_connector.open()
        return res

    def action_end(self,key,singal_data={},data={}):
        super(openobject_out, self).action_end(key,singal_data,data)
        if self.openobject_connector:
             self.openobject_connector.close()

    def process(self):
        #TODO : proper handle exception. not use generic Exception class
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
                        self.openobject_connector.execute('execute', self.model, 'import_data', self.fields_keys, [map(lambda x: d[self.fields[x]], self.fields_keys)])

                        yield d, 'main'
                    except Exception,e:
                        self.action_error(e)


if __name__ == '__main__':
    from etl_test import etl_test
    import etl
    openobject_conn=etl.connector.openobject_connector.openobject_connector('http://localhost:8069', 'dms_20090204', 'admin', 'admin',con_type='xmlrpc')
    test=etl_test.etl_component_test(openobject_out('test',openobject_conn,'res.partner'))
    test.check_input({'main':[{'name':'OpenERP1'},{'name':'Fabien1'}]})
    test.check_output([{'name':'OpenERP1'},{'name':'Fabien1'}],'main')
    res=test.output()
