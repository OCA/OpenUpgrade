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
    def __init__(self,name,fileconnector=None,transformer=None, dialect='excel', row_limit=0,bufsize=-1,encoding='utf-8', *args, **argv):
        super(csv_in, self).__init__(*args, **argv)  
        self.name=name      
        self.fileconnector = fileconnector 
        self.transformer=transformer
        self.dialect=dialect
        self.arg_values={}
        if argv.get('delimiter',False):
            self.arg_values['delimiter']=argv['delimiter']
        if argv.get('quotechar',False):
            self.arg_values['quotechar']=argv['quotechar']
        if argv.get('escapechar',False):
            self.arg_values['escapechar']=argv['escapechar']
        if argv.get('doublequote',False):
            self.arg_values['doublequote']=argv['doublequote']
        if argv.get('skipinitialspace',False):
            self.arg_values['skipinitialspace']=argv['skipinitialspace']
        if argv.get('lineterminator',False):
            self.arg_values['lineterminator']=argv['lineterminator']
        if argv.get('quoting',False):
            self.arg_values['quoting']=argv['quoting']

        self.row_limit=row_limit 
        self.row_count=0
        self.encoding=encoding
        self.bufsize=bufsize        
        
        self.fp=None
        self.reader=None
    
    def process(self):
        try:
            if not self.reader:
                if self.fileconnector:
                    self.fp=self.fileconnector.open('r',bufsize=self.bufsize)        
                else:
                    self.fp=open(self.name,'r',self.bufsize)
                self.reader=csv.DictReader(self.fp,dialect=self.dialect, **self.arg_values)                
                self.reader.fieldnames             
            for data in self.reader:
                self.row_count+=1
                if self.row_limit and self.row_count > self.row_limit:
                     raise StopIteration
                if self.transformer:
                    self.transformer.transform(data,encoding=self.encoding)
                yield data,'main'   
            if self.fileconnector:          
                self.fileconnector.close()
        except Exception,e:                                 
            yield e,'error'             
               
        

