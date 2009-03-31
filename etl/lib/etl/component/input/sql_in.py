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
sql_in

* Use to read data from sql db.

: Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>). All Rights Reserved
: GNU General Public License
"""

from etl.component import component
from etl.connector import sql_connector
import datetime

class sql_in(component):
    """
        This is an ETL Component that use to read data from sql db.

        Type: Data Component
        Computing Performance: Streamline
        Input Flows: 0
        * .* : nothing
        Output Flows: 0-x
        * .* : return the main flow with data from csv file
    """

    def __init__(self,sqlconnector,sqlquery,name='component.input.sql_in',transformer=None,row_limit=0):

	""" 
	Parameters
	sqlconnector :  Provides  sqlconnector connector to connect with file
	sqlquery     : TODO
	transformer  :  Provides transformer object to transform string data into  particular object
	row_limit    :  Limited records send to destination if row limit specified. If row limit is 0,all records are send.
	"""
        super(sql_in, self).__init__(name,transformer=transformer)

        self.sqlconnector = sqlconnector
        self.sqlquery=sqlquery
        self.row_limit=row_limit
        self.row_count=0


    def action_start(self,key,signal_data={},data={}):
        super(sql_in, self).action_start(key,signal_data,data)
        self.connector=self.sqlconnector.open()


    def action_end(self,key,signal_data={},data={}):
        super(sql_in, self).action_end(key,signal_data,data)
        self.sqlconnector.close()

    def process(self):
        try:
            cursor=self.connector.cursor()
            cursor.execute(self.sqlquery)
            print dir(cursor)
            columns_description= cursor.description
            rows= cursor.fetchall()
            for row in rows:
                self.row_count+=1
                if self.row_limit and self.row_count > self.row_limit:
                     raise StopIteration
                col_count=0
                d={}
                for column in columns_description:
                    d[column[0]]=row[col_count]
                    col_count+=1
                if self.transformer:
                    d=self.transformer.transform(d)
                if d:
                    yield d,'main'
        except TypeError,e:
            self.action_error(e)



