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
Data Map component
"""

from etl.component import component
import datetime

class data_map(component.component):
    """
        Data map component
    """   

    def __init__(self,name,map_criteria,transformer=None):
        super(data_map, self).__init__('(etl.component.transfer.data_map) '+name,transformer=transformer)         
        self.map_criteria = map_criteria
        

    def process(self):  
        #TODO : proper handle exception. not use generic Exception class      
        datas = []  
        
        for channel,trans in self.input_get().items():
            for iterator in trans:
                for d in iterator:
                    try:
                        if self.transformer:
                            d=self.transformer.transform(d)
                        
                        for map_data in self.map_criteria:
                             d[map_data['destination']]=eval(map_data['map_fun']+'('+d.pop(map_data['source'])+')')
                        
                                             
                        yield d, 'main'
                        
                    except Exception,e:  
                        print e
                        self.action_error(e)
