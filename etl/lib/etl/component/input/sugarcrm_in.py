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
This is an ETL Component that use to read data from sugarcrm.
"""

from etl.component import component
class sugarcrm_in(component):
    """
        This is an ETL Component that use to read data from Sugar CRM

    """
    def __init__(self, sugarcrm_connector, module, name='componet.input.sugarcrm_in', transformer=False, row_limit=0):
        """ 
        Required Parameters ::
    	sugarcrm_connector :  sugarcrm connector.
        module             : name of the module
        
        Extra Parameters ::
        name        : Name of Component.
    	transformer  : Transformer object to transform string data into particular type.
    	row_limit    : Limited records send to destination if row limit specified. If row limit is 0,all records are send.
        """

        super(sugarcrm_in, self).__init__(name, transformer=transformer)
        self.module=module
        self.sugarcrm_connector=sugarcrm_connector
        self.row_count=0
        self.row_limit=row_limit
        self.name = name

    def action_start(self, key, singal_data={}, data={}):
        super(sugarcrm_in, self).action_start(key, singal_data, data)
        self.connector = self.sugarcrm_connector.open()

    def process(self):
        res=[]
        res=self.sugarcrm_connector.search(self.module)
        for data in res:
            self.row_count+=1
            if self.row_limit and self.row_count > self.row_limit:
                 raise StopIteration
            if self.transformer:
                data=self.transformer.transform(data)
            if data:
                yield data, 'main'

    def __copy__(self):
        """
        Overrides copy method
        """
        res=sugarcrm_in(self.sugarcrm_connector, self.module, self.row_limit, self.name, self.transformer)
        return res
    



