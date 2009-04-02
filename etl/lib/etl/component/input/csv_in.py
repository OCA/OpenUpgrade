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
 To read data from csv file.

 Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>). 
 GNU General Public License
"""
from etl.component import component

class csv_in(component):
    """
    This is an ETL Component that use to read data from csv file.Its type is data component.
    Its computing peformance is streamline.It has two flows ::
    Input Flows: 0
    * .* : nothing
    Output Flows: 0-x
    * .* : return the main flow with data from csv file
    """

    def __init__(self,fileconnector,row_limit=0, csv_params={},name='component.input.csv_in',transformer=None):    
        """    
        Parameters:-
        fileconnector :  File connector is a L{localfile} to connect with file
        transformer   :  Provides transformer object to transform string data into  particular object
        row_limit     :  Limited records send to destination if row limit specified. If row limit is 0,all records are send.
        csv_param     :  To specify other csv parameter like fieldnames , restkey , restval etc. 
        """
        super(csv_in, self).__init__(name,transformer=transformer)
        self.fileconnector = fileconnector
        self.csv_params=csv_params
        self.row_limit=row_limit           

    def process(self):
        try:
            import csv
            fp=self.fileconnector.open()            
            reader=csv.DictReader(fp,**self.csv_params)             
            row_count=0           
            for data in reader:
                row_count+=1
                if self.row_limit and row_count > row_limit:
                     raise StopIteration
                if self.transformer:
                    data=self.transformer.transform(data)
                if data:
                    yield data,'main'            
            self.fileconnector.close(fp)        
        except Exception,e:
            self.signal('error',{'data':self.data,'type':'exception','error':str(e)})            
        except IOError,e:
            self.signal('error',{'data':self.data,'type':'exception','error':str(e)}) 

    def __copy__(self):        
        res= csv_in(self.fileconnector , self.row_limit, self.csv_params,self.name, self.transformer)
        return res

    
def test():
    pass
if __name__ == '__main__':
    test()


