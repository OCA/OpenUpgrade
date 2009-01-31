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
This is an ETL Component that use to read data from csv file.
"""

from etl import etl
from etl.connector import file_connector
import csv
import datetime

class csv_in(etl.component):
    """
        This is an ETL Component that use to read data from csv file.
       
        Type: Data Component
        Computing Performance: Streamline
        Input Flows: 0
        * .* : nothing
        Output Flows: 0-x
        * .* : return the main flow with data from csv file
    """
    _name='etl.component.input.csv_in'  
    _description='This is an ETL Component that use to read data from csv file.'   
    _author='tiny'

    def __init__(self,filename=None,fileconnector=None,transformer=None,row_limit=0,bufsize=-1, csv_params={}):
        super(csv_in, self).__init__(transformer=transformer)      
          
        self.fileconnector = fileconnector
        self.filename = filename
        self.row_limit=row_limit 
        self.row_count=0        
        self.bufsize=bufsize        
        self.csv_params=csv_params
        self.fp=None
        self.reader=None

    def action_start(self,key,singal_data={},data={}):
        try:
            super(csv_in, self).action_start(key,singal_data,data)
            if not self.reader:
                if self.fileconnector:
                    self.fp=self.fileconnector.open('r',bufsize=self.bufsize)        
                else:
                    self.fp=open(self.filename,'r',self.bufsize)
                self.reader=csv.DictReader(self.fp,**self.csv_params)                
                self.reader.fieldnames
        except Exception,e:                                                                    
            self.signal('error',{'error_msg': 'Error from start signal :'+str(e),'error_date':datetime.datetime.today()})

    def action_end(self,key,singal_data={},data={}):
        try:
            super(csv_in, self).action_end(key,singal_data,data)
            if self.fp:     
                 self.fp.close() 
            if self.fileconnector:    
                 self.fileconnector.close() 
        except Exception,e:                                                                    
            self.signal('error',{'error_msg': 'Error from end signal :'+str(e),'error_date':datetime.datetime.today()})

    def process(self):
        try:                         
            for data in self.reader:
                self.row_count+=1
                if self.row_limit and self.row_count > self.row_limit:
                     raise StopIteration
                try:
                    if self.transformer:
                        self.transformer.transform(data)
                except Exception,e:                                                                    
                    self.signal('error',{'error_msg':'Error from transform process :'+str(e),'error_date':datetime.datetime.today()})              
                yield data,'main'
            for stat in self.statitics.values():                
                yield stat,'statistics'  
            for error in self.errors:                
                yield error,'error'             
                               
        except Exception,e:                                                                    
            self.signal('error',{'error_msg':'Error from process :'+str(e),'error_date':datetime.datetime.today()})              
               
        

