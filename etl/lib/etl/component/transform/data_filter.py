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
Data filter component
"""

from etl.component import component
import datetime

class data_filter(component):
    """
        Data filter component
    """   

    def __init__(self,filter_criteria,name='component.transfer.data_filter',transformer=None):

        """ 
        Parameters ::

        transformer      :  provides transformer object to transform string data into  particular object
        filter_crtiteria :  TODO
        """
        super(data_filter, self).__init__(name,transformer=transformer)         
        self.filter_criteria = filter_criteria          

    def process(self):  
        #TODO : proper handle exception. not use generic Exception class      
        datas = []  
        
        for channel,trans in self.input_get().items():
            for iterator in trans:
                for d in iterator:
                    try:
                        if self.transformer:
                            d=self.transformer.transform(d)
                        filter=''
                        for filter_data in self.filter_criteria: 
                             val = d[filter_data['name']]                                                                                                             
                             _filter = filter_data.get('filter',False)                             
                             if val and _filter:
                                 val=eval((_filter) % d)                                
                             filter += " %s %s %s %s" % (repr(val),filter_data['operator'],filter_data['operand'],filter_data.get('condition',''))
                        
                        if self.transformer:
                            d=self.transformer.transform(d)
                        if eval(filter):                        
                           yield d, 'main'
                        else:
                           yield d, 'invalid'
                    except NameError,e:                          
                        self.action_error(e)
