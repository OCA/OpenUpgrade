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
 To write data to csv file.

 Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>).
 GNU General Public License
"""

from etl.component import component


class csv_out(component):
    """
    This is an ETL Component that writes data to csv file.

    Type                   : Data Component.
    Computing Performance  : Streamline.
    Input Flows            : 0-x.
    * .*                   : The main data flow with input data.
    Output Flows           : 0-1.
    * main                 : Return all data.
    """

    def __init__(self, fileconnector, csv_params={}, name='component.output.csv_out', transformer=None, row_limit=0):
        """
        Required  Parameters
        fileconnector   :  Localfile connector.

        Extra Parameters 
        name            : Name of Component.
        transformer     : Transformer object to transform string data into  particular object.
        row_limit       : Limited records are sent to destination if row limit is specified. If row limit is 0, all records are sent.
        csv_param       : To specify other csv parameter like fieldnames , restkey , restval etc.
        """
        super(csv_out, self).__init__(name=name, connector=fileconnector, transformer=transformer, row_limit=row_limit)
        self._type = 'component.output.csv_out'
        self.csv_params = csv_params

    def __copy__(self):
        res = csv_out(self.connector , self.csv_params, self.name, self.transformer, self.row_limit)
        return res

    def end(self):
        super(csv_out, self).end()
        if self.fp:
            self.connector.close(self.fp)
            self.fp = False

    def process(self):
        import csv
        datas = []
        self.fp = False
        writer = False
        for channel, trans in self.input_get().items():
            for iterator in trans:
                for d in iterator:
                    if not self.fp:
                        self.fp = self.connector.open('wb+')
                        fieldnames = d.keys()
                        writer = csv.DictWriter(self.fp, fieldnames)
                        writer.writerow(dict(map(lambda x: (x, x), fieldnames)))
                    writer.writerow(d)
                    yield d, 'main'

def test():
    from etl_test import etl_test
    import etl
    file_conn = etl.connector.localfile('../../../demo/input/partner1.csv')
    test = etl_test.etl_component_test(csv_out(file_conn, name='csv test'))
    test.check_input({'main': [{'tel': '+32.81.81.37.00', 'id': '11', 'name': 'Fabien11'}]})
    test.check_output([{'tel': '+32.81.81.37.00', 'id': '11', 'name': 'Fabien11'}], 'main')
    res = test.output()
    print res

if __name__ == '__main__':
    test()

