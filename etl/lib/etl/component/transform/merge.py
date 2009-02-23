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
   This is an ETL Component that use to display log detail in streamline.
"""

from etl.component import component
import sys
class merge(component.component):
    """
        This is an ETL Component that merge all input flows into only one ouput flow.

        Type: Data Component
        Computing Performance: Streamline
        Input Flows: 0-x
        * .* : the main data flow with input data
        Output Flows: 1
        * .* : return the main flow 
    """    


    def process(self):
        #TODO : proper handle exception
        for channel, list_trans in self.input_get().items():
            my_gen_list = []
            for generator in list_trans:
                my_gen_list.append(generator)
        p = 0
        has_yield = False
        while True:
            if p == len(my_gen_list):
                p = 0
                has_yield = False
            try:
                data = my_gen_list[p].next()
            except:
                p += 1
                if not has_yield and p == len(my_gen_list):
                    break
                continue
            if data:
                yield data, 'main'
                has_yield = True
                p += 1
