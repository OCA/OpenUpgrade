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
This is an ETL Component that use to write data into sql table.
"""

from etl.component import component
import datetime

class sql_out(component.component):
    """
        This is an ETL Component that use to write data into sql table.

        Type: Data Component
        Computing Performance: Streamline
        Input Flows: 0-x
        * .* : the main data flow with input data
        Output Flows: 0-1
        * main : return all data
    """   

    def __init__(self,name,sqlconnector,sqltable,transformer=None,row_limit=0):
        super(sql_out, self).__init__('(etl.component.output.sql_out) '+name,transformer=transformer)      
          
        self.sqlconnector = sqlconnector 
        self.sqltable=sqltable    
        self.row_limit=row_limit 
        self.row_count=0                                
         

    def action_end(self,key,singal_data={},data={}):        
        super(sql_out, self).action_end(key,singal_data,data)        
        if self.sqlconnector:    
             self.sqlconnector.close()        

    def process(self):  
        #TODO : proper handle exception. not use generic Exception class      
        datas = []        
        for channel,trans in self.input_get().items():
            for iterator in trans:
                for d in iterator:
                    try:                    
                        if not self.connector:
                            self.connector=self.sqlconnector.open()
                        if self.transformer:
                            d=self.transformer.transform(d)
                        insert_query=' INSERT into %s (%s) VALUES (%s)' % (self.sqltable,','.join(d.keys()),','.join(d.values()))
                        self.connector.cursor.execute(insert_query)                      
                        
                        yield d, 'main'
                    except Exception,e:  
                        print e
                        self.action_error(e)
