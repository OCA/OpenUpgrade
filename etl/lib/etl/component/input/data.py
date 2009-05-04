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
 This component is used to read data.

 Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>).
 GNU General Public License
"""


from etl.component import component


class data(component):
    """
        This is an ETL Component that return python data from a list of dictionary.
    """

    def __init__(self, datas, name='component.input.data', transformer=None, row_limit=0):
        """
        Required  Parameters
        datas      : Input data

        Extra Parameters
        name          : Name of Component.
        transformer   : Transformer object to transform string data into  particular object.
       """
        super(data, self).__init__(name=name, transformer=transformer, row_limit=row_limit)
        self._type = 'component.input.data'
        self.datas = datas

    def __copy__(self):
        res = data(self.datas, self.name, self.transformer, self.row_limit)
        return res

    def process(self):
        for d in self.datas:
            yield d, 'main'



def test():
    from etl_test import etl_test
    import etl
    inp_data = etl.component.input.data([
        {'id': 1, 'name': 'Fabien', 'country_id': 3},
        {'id': 2, 'name': 'Luc', 'country_id': 3},
        {'id': 3, 'name': 'Henry', 'country_id': 1}
    ])
    test = etl_test.etl_component_test(inp_data)
    test.check_output([{'country_id': 3, 'id': 1, 'name': 'Fabien'}, {'country_id': 3, 'id': 2, 'name': 'Luc'}, {'country_id': 1, 'id': 3, 'name': 'Henry'}] )
    res = test.output()
    print res

if __name__ == '__main__':
    test()
