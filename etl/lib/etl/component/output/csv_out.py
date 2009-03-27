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
csv_out
*  Use to write data to csv file.

: Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>). All Rights Reserved
: GNU General Public License
"""

from etl.component import component
import csv
import datetime

class csv_out(component):
    """
        This is an ETL Component that use to write data to csv file.

        Type: Data Component
        Computing Performance: Streamline
        Input Flows: 0-x
        * .* : the main data flow with input data
        Output Flows: 0-1
        * main : return all data
    """   

    def __init__(self,fileconnector,transformer=None,name='component.output.csv_out',row_limit=0, csv_params={}):

	""" 
    Paramters ::

	fileconnector : Provides  localfile connector to connect with file
	transformer   : Provides transformer object to transform string data into  particular object
	row_limit     : Limited records send to destination if row limit specified. If row 	limit is 0,all records are send.
	csv_param     : To specify other csv parameter like fieldnames , restkey , restval etc. 

	"""
        super(csv_out, self).__init__(name,transformer=transformer)      
          
        self.fileconnector = fileconnector 
        self.csv_params=csv_params       
        self.row_limit=row_limit 
        self.row_count=0                                
        self.fp=None
        self.writer=None   

    def action_end(self,key,singal_data={},data={}):        
        super(csv_out, self).action_end(key,singal_data,data)
        if self.fp:     
             self.fp.close() 
        if self.fileconnector:    
             self.fileconnector.close()        

    def process(self):  
        #TODO : proper handle exception. not use generic Exception class      
        datas = []        
        for channel,trans in self.input_get().items():
            for iterator in trans:
                for d in iterator:
                    try:                    
                        if not self.fp:
                            self.fp=self.fileconnector.open('wb+')
                            fieldnames = d.keys()
                            self.writer = csv.DictWriter(self.fp, fieldnames)
                            self.writer.writerow(dict(map(lambda x: (x,x), fieldnames)))
                        self.writer.writerow(d)
                        yield d, 'main'
                    except IOError,e:  
                        self.action_error(e)



def test():
    from etl_test import etl_test
    import etl
    file_conn=etl.connector.file_connector('http://localhost:8069', 'dms_20090204', 'admin', 		              
    'admin',con_type='xmlrpc')
    test=etl_test.etl_component_test(csv_out('test',file_conn,'res.partner'))
    test.check_input({'main':[{'name':'OpenERP1'},{'name':'Fabien1'}]})
    test.check_output([{'name':'OpenERP1'},{'name':'Fabien1'}],'main')
    res=test.output()
if __name__ == '__main__':
    test()


