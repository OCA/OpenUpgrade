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

class data_filter(component.component):
    """
        Data filter component
    """   

    def __init__(self,name,where_criteria,transformer=None):
        super(data_filter, self).__init__('(etl.component.transfer.data_filter) '+name,transformer=transformer)         
        self.where_criteria = where_criteria          

    def process(self):  
        #TODO : proper handle exception. not use generic Exception class      
        datas = []  
        
        for channel,trans in self.input_get().items():
            for iterator in trans:
                for d in iterator:
                    try:
                        if self.transformer:
                            d=self.transformer.transform(d)
                        where=''
                        for where_data in self.where_criteria:
                             where += ' %s %s % %s' % (d[where_data['field']],where_data['operator'],eval(where_data['operand']),where_data['condition'])
                        if eval(where):                        
                           yield d, 'main'
                        else:
                           yield d, 'invalid'
                    except Exception,e:  
                        print e
                        self.action_error(e)
