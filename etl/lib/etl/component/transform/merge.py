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
 To merge all input flows.

 Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>). 
 GNU General Public License
"""

from etl.component import component
import sys

class merge(component):
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
        my_gen_list = []
        for list_trans in self.input_get().values():
            my_gen_list += list_trans
        p = -1
        while my_gen_list:
            p = (p+1) % len(my_gen_list)
            try:
                data = my_gen_list[p].next()
                yield data, 'main'
            except StopIteration, e:
                del my_gen_list[p]
                p = 0

if __name__=='__main__':
    # implement blackbox test
    # Input:
    #   'main': [{'name':'test'}], 'second': [{'name':'test2'}]
    # Output:
    #   'concat'
    pass
