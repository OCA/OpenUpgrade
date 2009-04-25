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
  To read data from sql db.

 Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>). 
 GNU General Public License
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

    def __init__(self, sqlconnector, sqlquery, name='component.input.sql_in', transformer=None, row_limit=0):

        """ 
        Required Parameters ::
        sqlconnector :  sqlconnector connector.
        sqlquery     : SQL Query
        
        Extra Parameters ::
        name        : Name of Component.
        transformer  : Transformer object to transform string data into particular type.
        row_limit    : Limited records send to destination if row limit specified. If row limit is 0,all records are send.
        """
        super(sql_in, self).__init__(name=name,connector=sqlconnector, transformer=transformer, row_limit=row_limit)        
        self._type='component.input.sql_in'
        self.sqlquery=sqlquery
        
        
    def __copy__(self):       
        res=sql_in(self.connector, self.sqlquery, self.name, self.transformer, self.row_limit)
        return res

   


    def end(self):
        super(sql_in, self).end()
        if self.sql_con:
            self.connector.close(self.sql_con)
            self.sql_con=False

    def process(self):        
        self.sql_con=self.connector.open()
        cursor=self.sql_con.cursor()
        cursor.execute(self.sqlquery)            
        columns_description= cursor.description
        rows= cursor.fetchall()
        for row in rows:               
            col_count=0
            d={}
            for column in columns_description:
                d[column[0]]=row[col_count]
                col_count+=1                
            if d:
                yield d, 'main'
       
        
   
    

