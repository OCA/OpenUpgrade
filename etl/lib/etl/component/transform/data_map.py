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
Data Map component.
"""

from etl.component import component
import datetime
from etl import tools

class map(component):
    """
        Data map component.
    """

    def __init__(self, map_criteria, preprocess=None, name='component.transfer.map', transformer=None, row_limit=0):
        """ 
        Required Parameters    
        map_criteria  :  Mapping criteria.
        
        Extra Parameters 
        name          : Name of the component.
        transformer   : Transformer object to transform string data into  particular object.
        preprocess    : For initializing the instance of custom variable.
        """
        
        super(map, self).__init__(name=name, transformer=transformer, row_limit=row_limit)
        self._type = 'component.transfer.map'
        self.map_criteria = map_criteria
        self.preprocess = preprocess

    def __copy__(self):        
        res = map(self.map_criteria, self.preprocess, self.name, self.transformer, self.row_limit)
        return res
        
    def process(self):        
        channels = self.input_get()
        datas = {}
        if self.preprocess:
            datas = self.preprocess(self, channels)
        for channel, trans in channels.items():            
            for iterator in trans:                
                for d in iterator:                    
                    for channel_dest, channel_value in self.map_criteria.items():
                        result = {}
                        for key, val in channel_value.items():
                            if val:
                                datas['main'] = d
                                datas['tools'] = tools
                                result[key] = eval(val, datas)
                            else:
                                result[key] = val
                        if self.transformer:
                            result = self.transformer.transform(result)
                        yield result, channel_dest

def test():

    from etl_test import etl_test
    input_part = [
    {'id': 1, 'name': 'Fabien', 'country_id': 3}, 
    {'id': 2, 'name': 'Luc', 'country_id': 3}, 
    {'id': 3, 'name': 'Henry', 'country_id': 1}
    ]
    input_cty = [{'id': 1, 'name': 'Belgium'}, {'id': 3, 'name': 'France'}]
    map_keys = {'main': {
    'id': "main['id']", 
    'name': "main['id'].upper()", 
    'country': "country_var[main['country_id']]['name']"
    }}
    def preprocess(self, channels):
        cdict = {}
    for trans in channels['country']:
        for iterator in trans:
            for d in iterator:
                cdict[d['id']] = d
    return {'country_var': cdict}
    test = etl_test.etl_component_test(map(map_keys, preprocess))
    test.check_input({'partner':input_part, 'countries': input_cty})
    print test.output()

if __name__ == '__main__':
	test()
