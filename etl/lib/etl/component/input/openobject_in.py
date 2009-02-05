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
This is an ETL Component that use to read data from open object model.
"""

from etl.component import component
from etl.connector import openobject_connector
import datetime

class openobject_in(component.component):
    """
        This is an ETL Component that use to read data from open object model.
       
        Type: Data Component
        Computing Performance: Streamline
        Input Flows: 0
        * .* : nothing
        Output Flows: 0-x
        * .* : return the main flow with data from csv file
    """    

    def __init__(self,name,openobject_connector,model,domain=[],fields=[],context={},transformer=None,row_limit=0):
        super(openobject_in, self).__init__('(etl.component.input.sql_in) '+name,transformer=transformer)      
          
        self.openobject_connector = openobject_connector  
        self.model=model             
        self.domain=domain 
        self.context=context
        self.fields=fields
        self.row_limit=row_limit                            
        

    def action_start(self,key,singal_data={},data={}):        
        super(openobject_in, self).action_start(key,singal_data,data)                
        self.connector=self.sqlconnector.open()                
                                         

    def action_end(self,key,singal_data={},data={}):        
        super(openobject_in, self).action_end(key,singal_data,data)       
        if self.openobject_connector:    
             self.openobject_connector.close()         

    def process(self):        
        try:
            ids = self.openobject_connector.execute('/object', 'execute',
                        self.model, 'search', self.domain,limit=self.row_limit ,context=self.context)
            rows = self.openobject_connector.execute('/object', 'execute',
                        self.model, 'export_data', ids,self.fields, self.context)
            for row in rows:                                
                self.row_count+=1
                if self.row_limit and self.row_count > self.row_limit:
                     raise StopIteration                                        
                if self.transformer:
                    row=self.transformer.transform(row)
                if row:
                    yield row,'main'                                                                                   
        except TypeError,e:
            self.action_error(e)
        except IOError,e:
            self.action_error(e)
            
               
        

