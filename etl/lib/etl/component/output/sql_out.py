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
 To write data into sql table.

 Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>). 
 GNU General Public License

"""

from etl.component import component
import datetime

class sql_out(component):
    """
        This is an ETL Component that use to write data into sql table.

        Type: Data Component
        Computing Performance: Streamline
        Input Flows: 0-x
        * .* : the main data flow with input data
        Output Flows: 0-1
        * main : return all data
    """   

    def __init__(self,sqlconnector,sqltable,name='component.output.sql_out',transformer=None,row_limit=0):

	""" 
    Parameters ::    
	sql_connector : Provides  sql connector to connect with file
	sqltable      : Provides the name of the sql table
	transformer   : Provides transformer object to transform string data into   particular object
	row_limit     : Limited records send to destination if row limit specified. If row limit is 0,all records are send.
        """
        super(sql_out, self).__init__(name,transformer=transformer)      
          
        self.sqlconnector = sqlconnector 
        self.sqltable=sqltable    
        self.row_limit=row_limit 
        self.row_count=0                                
        self.connector=False 

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
                        insert_query=" INSERT into %s (%s) VALUES (%s)" % (self.sqltable,','.join(d.keys()),','.join(map(lambda x:(type(x) in (int,long,float,complex)) and x or repr(str(x)),d.values())))                        
                        cr=self.connector.cursor()
                        cr.execute(insert_query)                     
                        self.connector.commit()                       
                        yield d, 'main'
                    except IOError,e:                          
                        self.action_error(e)
  

def test():
    from etl_test import etl_test
    import etl
    sql_conn=etl.connector.sql_connector.sql_connector('localhost',5432, 'dms_20090204', 'postgres', 'postgres')
    test=etl_test.etl_component_test(sql_out('test',sql_conn,'res_partner'))
    test.check_input({'main':[{'name':'OpenERP11'},{'name':'Fabien11'}]})
    test.check_output([{'name':'OpenERP11'},{'name':'Fabien11'}],'main')
    res=test.output()

if __name__ == '__main__':  
    test()
