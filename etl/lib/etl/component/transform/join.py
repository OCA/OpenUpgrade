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
Data Join component.
"""

from etl.component import component
from etl.component.transform import map
import datetime
from etl import tools

class join(map):
    """
        Data Join component.
    """

    def __init__(self, map_criteria, join_keys={}, name='component.transfer.join', transformer=None, row_limit=0):

        """
        Required Parameters
        map_criteria   :  Mapping criteria.

        Extra Parameters
        name          : Name of the component.
        join_keys     :
        transformer   : Transformer object to transform string data into  particular object.
        """
        super(join, self).__init__(map_criteria, None, name, transformer, row_limit)
        self._type = 'component.transfer.join'
        self.map_criteria = map_criteria
        self.join_keys = join_keys

        def preprocess(self, channels):
            res = {}
            for chn in join_keys:
                cdict = {}
                for iterator in channels[chn]:
                    for d in iterator:
                        cdict[d[join_keys[chn]]] = d
                    res[chn] = cdict
            return res
        self.preprocess = preprocess

    def __copy__(self):
        res = join(self.map_criteria, self.join_keys, self.name, self.transformer, self.row_limit)
        return res

    


def test():
    from etl_test import etl_test
    import etl
    input_part = [
        {'id': 1, 'name': 'Fabien', 'country_id': 3},
        {'id': 2, 'name': 'Luc', 'country_id': 3},
        {'id': 3, 'name': 'Henry', 'country_id': 1}
    ]
    input_cty = [{'id': 1, 'name': 'Belgium'}, {'id': 3, 'name': 'France'}]
    map_keys = {'main': {
        'id': "main['id']",
        'name': "main['id'].upper()",
        'country': "country[main['country_id']]['name']"
    }}
    join_keys = {
         'country': 'id'
    }
    test = etl_test.etl_component_test(join(map_keys, join_keys))
    test.check_input({'partner':input_part, 'countries': input_cty})
    print test.output()

if __name__ == '__main__':
    test()

