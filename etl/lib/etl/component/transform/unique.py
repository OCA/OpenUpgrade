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
  To perform unique operation.

 Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>). 
 GNU General Public License
"""

from etl.component import component
class unique(component):
    """
        This is an ETL Component that use to perform unique.
 
        Type: Data Component
        Computing Performance: Semi-Streamline
        Input Flows: 1
        * .* : the main data flow with input data
        Output Flows: 0-x
        * .* : return the main flow with unique Result
        * .* : return the duplicate flow with duplicate Result
    """    

    def __init__(self,name='component.transform.unique'):
        super(unique, self).__init__(name )



    def process(self):
        unique_datas=[]
        duplicate_datas=[]
        for channel,trans in self.input_get().items():
            for iterator in trans:                
                for d in iterator:
                   if d in unique_datas:                       
                       yield d, "duplicate"		                    
                   else :
                       unique_datas.append(d)
        for d in unique_datas:
            yield d, "main"
        


def test():                           

    from etl_test import etl_test
    from etl import transformer
    input_part = [
        {'id': 1L, 'name': 'Fabien','active': True,'birth_date':'2009-02-01','amount':209.58},
        {'id': 1L, 'name': 'Fabien','active': True,'birth_date':'2009-02-01','amount':209.58},
        {'id': 3L, 'name': 'Henry','active': True,'birth_date':'2006-02-01','amount':219.20},
    ]   
    unique_part = [
        {'id': 1L, 'name': 'Fabien','active': True,'birth_date':'2009-02-01','amount':209.58},        
        {'id': 3L, 'name': 'Henry','active': True,'birth_date':'2006-02-01','amount':219.20},
    ] 
    duplicate_part = [
        {'id': 1L, 'name': 'Fabien','active': True,'birth_date':'2009-02-01','amount':209.58},                
    ]     
    test=etl_test.etl_component_test(unique())
    test.check_input({'main':input_part})    
    test.check_output(duplicate_part,'duplicate')
    print test.output()

if __name__ == '__main__':
    test()
