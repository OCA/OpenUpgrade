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
 Sub job component.

 Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>).
 GNU General Public License
"""
import etl
from etl.component import component

class subjob(component):
    """
    Sub job component.
    """   
    def __init__(self, sub_job, name='component.transform.subjob'):
        super(subjob, self).__init__(name=name)
        self._type='component.transform.subjob'
        self.sub_job = sub_job        

    def __copy__(self):        
        res = subjob(self.sub_job, name = self.name)
        return res
    
    def dummy_iterator(self, channel, datas):
        for d in datas:            
            yield d, channel

    def dummy2_iterator(self, dummy2):
        self.result = {}
        for channel,trans in dummy2.input_get().items():
            self.result.setdefault(channel, [])
            for iterator in trans:                
                for d in iterator:                    
                    self.result[channel].append(d)  
                    yield d, channel

    def process(self):          
        dummy = etl.component.component(name='dummy')
        start_coms = []
        for com in self.sub_job.get_components():
            if com.is_start():
                start_coms.append(com)
            com.generator = False

        dummy2 = etl.component.component(name='dummy')
        end_coms = []
        for com in self.sub_job.get_components():
            if com.is_end():
                end_coms.append(com)
            com.generator = False
        self.sub_job.add_component(dummy)  
        self.sub_job.add_component(dummy2) 
     
        for start_com in start_coms:
            tran = etl.transition(dummy,start_com) 
        for end_com in end_coms:
            tran = etl.transition(end_com, dummy2)  
        dummy2.generator =  self.dummy2_iterator(dummy2)
            

        for channel,trans in self.input_get().items():
            for iterator in trans:   
                self.result = {}            
                if dummy:
                    dummy.generator = self.dummy_iterator(channel,iterator)                    
                    self.sub_job.run()  
                                   
                for channel,iterator in self.result.items():                   
                    for d in iterator:                        
                        yield d, channel      

    
    
