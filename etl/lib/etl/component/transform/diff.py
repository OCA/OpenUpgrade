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
This is an ETL Component that use to find diff.
"""

from etl.component import component

class diff(component):
    """
        This is an ETL Component that use to find diff.
        Takes 2 flows in input and detect a difference between these two flows
        using computed keys (based on data records) to compare elements that may not
        have to be in the same order.

        Type: Data Component
        Computing Performance: Semi-Streamline
        Input Flows: 2
        * main: The main flow
        * .*: the second flow
        Output Flows: 0-x
        * same: return all elements that are the same in both input flows
        * updated: return all updated elements
        * removed: return all elements that where in main and not in the second flow
        * added: return all elements from the second flow that are not in main channel
    """
    def __init__(self, keys,name=''):
        self.keys = keys
        self.row = {}
        self.diff = []
        self.same = []
        super(diff, self).__init__('(etl.component.process.diff) '+name)

    # Return the key of a row
    def key_get(self, row):
        result = []
        for k in self.keys:
            result.append(row[k])
        return tuple(result)

    def process(self):
        #TODO : put try..except block
        self.row = {}
        for channel,transition in self.input_get().items():
            if channel not in self.row:
                self.row[channel] = {}
            other = None
            for key in self.row.keys():
                if key<>channel:
                    other = key
                    break
            for iterator in transition:
                for r in iterator:
                    key = self.key_get(r)
                    if other and (key in self.row[other]):
                        if self.row[other][key] == r:
                            yield r, 'same'
                        else:
                            yield r, 'update'
                        del self.row[other][key]
                    else:
                        self.row[channel][key] = r
        todo = ['add','remove']
        for k in self.row:
            channel= todo.pop()
            for v in self.row[k].values():
                yield v,channel
