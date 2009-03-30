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
schema_validator 

*  use to perform Schema Validation.

: Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>). All Rights Reserved
: GNU General Public License
"""
import types
from etl.component import component
import datetime
import time
class schema_validator(component):
    """
        This is an ETL Component that use to perform Schema Validation.
 
        Type: Data Component
        Computing Performance: Semi-Streamline
        Input Flows: 1
        * .* : the main data flow with input data
        Output Flows: 0-x
        * .* : return the main flow with Schema Validation Result
        * invalid_field : return data which has more or less fields
        * invalid_name  : return data which has wrong field name
        * invalid_key   : return data which has not match unique contraint
        * invalid_null  : return data which has not match null contraint
        * invalid_type  : return data that fields have invalid type
        * invalid_size  : return data which has more size
        * invalid_format : return data which has not match with format
        
    """    

    def __init__(self,schema,name='component.transform.schema_validator'):
        super(schema_validator, self).__init__(name )
        self.schema = schema



    def process(self):        
        for channel,trans in self.input_get().items():
            for iterator in trans:       
                keys=[]                         
                for d in iterator:                                        
                    if len(d.keys())!=len(self.schema.keys()):                        
                        yield d,'invalid_field'
                    else:
                        channel='main'                                            
                        for f in d:                        
                            if f not in self.schema:
                                channel='invalid_name'                        
                                break
                            if self.schema[f].get('key',False):                                
                                if not d[f]:
                                    channel="invalid_key"
                                    break
                                if d[f] in keys:                                                               
                                    channel="invalid_key"
                                    break                                
                                keys.append(d[f])

                            if self.schema[f].get('Is_NULL',False):                                    
                                if not d[f]:
                                    channel="invalid_null"                            
                                    break

                            if self.schema[f].get('type',False):                                
                                if type(d[f]) != eval(self.schema[f]['type']):
                                    channel='invalid_type'
                                    break

                            if self.schema[f].get('format',False):
                            # TODO : improve this, 
                            # USE  : check format using input mask validation or regular expression
                                if self.schema[f]['type'] == "datetime.date" :
                                    try :
                                        a = time.strptime(str(d[f]),self.schema[f]['format']) 
                                    except ValueError ,e:
                                        channel="invalid_format"						
                                        break
                            if self.schema[f].get('size',False):                                
                                if len(d[f]) > int(self.schema[f]['size']):
                                    channel='invalid_size'
                                    break
                            
                        yield d,channel
                           


def test():
    from etl_test import etl_test
    from etl import transformer
    input_part = [
        {'id': 1L, 'name': 'Fabien','active': True,'birth_date':'2009-02-01','amount':209.58},
        {'id': 2L, 'name': 'Luc','active': True,'birth_date':'2007-02-01','amount':211.25},
        {'id': 3L, 'name': 'Henry','active': True,'birth_date':'2006-02-01','amount':219.20},
    ]    
    schema= {
		'id':{'type':'long','key':True,'Is_Null':True},
		'name':{'type':'str','size':'10','Is_NULL':False},
		'active':{'type':'bool','Is_NULL':False},
    	        'birth_date':{'type':'datetime.date','Is_NULL':False,'format':'%y-%m-%d'},
		'amount':{'type':'float','Is_NULL':True}
	}    
    test=etl_test.etl_component_test(schema_validator(schema))
    test.check_input({'main':input_part})
    print test.output()

if __name__ == '__main__':
    test()

