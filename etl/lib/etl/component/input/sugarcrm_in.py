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

        super(sugarcrm_in, self).__init__(name=name,connector=sugarcrm_connector, transformer=transformer,row_limit=row_limit)
        self._type='componet.input.sugarcrm_in'
        self.module=module

    def __copy__(self):
        res=sugarcrm_in(self.sugarcrm_connector, self.module, self.name, self.transformer, self.row_limit)
        return res

    def process(self):
        res=[]
        (portType, session_id,)=self.connector.open()
        res=self.connector.search(portType, session_id,self.module)
        for data in res:
            if data:
                print data['first_name'],data['account_name']
                yield data, 'main'






