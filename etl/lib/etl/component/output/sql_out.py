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
 To write data into SQL table.

 Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>).
 GNU General Public License.

"""

from etl.component import component
import datetime

class sql_out(component):
    """
        This is an ETL Component that writes data in SQL table.

        Type                   : Data Component.
        Computing Performance  : Streamline.
        Input Flows            : 0-x.
        * .*                   : The main data flow with input data.
        Output Flows           : 0-1.
        * main                 : Return all data.
    """

    def __init__(self, sqlconnector, sqltable, name='component.output.sql_out', transformer=None, row_limit=0):

        """
        Required  Parameters
        sql_connector  : SQL connector.
        sqltable       : The name of the SQL table.

        Extra Parameters
        name           : Name of Component.
        transformer    : Transformer object to transform string data into   particular object.
        row_limit      : Limited records are sent to destination if row limit is specified. If row limit is 0, all records are sent.
        """
        super(sql_out, self).__init__(name=name, connector=sqlconnector, transformer=transformer, row_limit=row_limit)
        self._type = 'component.output.sql_out'
        self.sqltable = sqltable

    def __copy__(self):
        res = sql_out(self.connector, self.sqlquery, self.name, self.transformer, self.row_limit)
        return res

    def end(self):
        super(sql_out, self).end()
        if self.sqlconnector:
             self.connector.close(self.sqlconnector)

    def process(self):
        datas = []
        self.sqlconnector = False
        for channel, trans in self.input_get().items():
            for iterator in trans:
                for d in iterator:
                    if not self.sqlconnector:
                        self.sqlconnector = self.connector.open()
                    insert_query = " INSERT into %s (%s) VALUES (%s)" % (self.sqltable, ','.join(d.keys()), ','.join(map(lambda x: (type(x) in (int, long, float, complex)) and x or repr(str(x)), d.values())))
                    cr = self.sqlconnector.cursor()
                    cr.execute(insert_query)
                    self.sqlconnector.commit()
                    yield d, 'main'

def test():
    from etl_test import etl_test
    import etl
    sql_conn = etl.connector.sql_connector('localhost', 5432, 'trunk', 'postgres', 'postgres')
    test = etl_test.etl_component_test(sql_out(sql_conn, 'res_partner'))
    test.check_input({'main': [{'name': 'tinyerp belgium'}]})
    test.check_output([{'name': 'tinyerp belgium'}], 'main')
    res = test.output()
    print res

if __name__ == '__main__':
    test()
