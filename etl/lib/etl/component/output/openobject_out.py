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
This is an ETL Component that use to write data into openobject model.
"""

from etl.component import component
import datetime

class openobject_out(component.component):
    """
        This is an ETL Component that use to write data into sql table.

        Type: Data Component
        Computing Performance: Streamline
        Input Flows: 0-x
        * .* : the main data flow with input data
        Output Flows: 0-1
        * main : return all data
    """   

    def __init__(self,name,openobject_connector,model,transformer=None):
        super(openobject_out, self).__init__('(etl.component.output.openobject_out) '+name,transformer=transformer)      
          
        self.openobject_connector = openobject_connector 
        self.model=model
        self.connector=False 

    def action_end(self,key,singal_data={},data={}):        
        super(openobject_out, self).action_end(key,singal_data,data)        
        if self.openobject_connector:  
             self.openobject_connector.logout()  
             self.openobject_connector.close()        

    def process(self):  
        #TODO : proper handle exception. not use generic Exception class      
        datas = []        
        for channel,trans in self.input_get().items():
            for iterator in trans:
                for d in iterator:
                    try:                    
                        if not self.connector:
                            self.connector=self.openobject_connector.open()
                            self.openobject_connector.login()
                        if self.transformer:
                            d=self.transformer.transform(d)                        
                        self.openobject_connector.execute('execute', self.model, 'import_data', d.keys(), [d.values()])                 
                        
                        yield d, 'main'
                    except Exception,e:  
                        print e
                        self.action_error(e)


if __name__ == '__main__':    
    from etl_test import etl_test
    import etl
    openobject_conn=etl.connector.openobject_connector.openobject_connector('http://localhost:8069', 'dms_20090204', 'admin', 'admin',con_type='xmlrpc')
    test=etl_test.etl_component_test(openobject_out('test',openobject_conn,'res.partner'))
    test.check_input({'main':[{'name':'OpenERP1'},{'name':'Fabien1'}]})
    test.check_output([{'name':'OpenERP1'},{'name':'Fabien1'}],'main')
    res=test.output()
