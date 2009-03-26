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
import socket
import xmlrpclib
import datetime
import time
class facebook_in(component):
    """
        This is an ETL Component that use to read data from facebook.
       
        Type: Data Component
        Computing Performance: Streamline
        Input Flows: 0
        * .* : nothing
        Output Flows: 0-x
        * .* : return the main flow with data
    """    

    def __init__(self,facebook_connector,method,domain=[],fields=['name'],name='component.input.facebook_in',transformer=None,row_limit=0):
        super(facebook_in, self).__init__(name,transformer=transformer)      
        self.facebook_connector = facebook_connector  
        self.method=method
        self.domain=domain
        self.fields=fields
        self.row_limit=row_limit
        self.facebook = None

    def action_start(self,key,singal_data={},data={}):        
        super(facebook_in, self).action_start(key,singal_data,data)                
        self.facebook=self.facebook_connector.open()  
                                        

    def action_end(self,key,singal_data={},data={}):        
        super(facebook_in, self).action_end(key,singal_data,data)       
        if self.facebook_connector:  
            self.facebook_connector.close()
            self.facebook=False     

    def process(self):
        rows=[]                                
        if self.method=='get_friends':
            friends = self.facebook.friends.get()
            rows = self.facebook.users.getInfo(friends, self.fields)                       
        for row in rows:                           
            if self.transformer:
                row=self.transformer.transform(row)
            if row:
                print row
                yield row,'main'  

def test():
    from etl_test import etl_test
    import etl
    facebook_conn=etl.connector.facebook_connector('http://facebook.com', 'modiinfo@gmail.com', '20')
    test1=etl_test.etl_component_test(facebook_in(facebook_conn,'get_friends', fields=['name', 'birthday']))
    res=test1.output() 
    print "/>>",res
if __name__ == '__main__':
    test()                                                                       
        
                    
               
        

