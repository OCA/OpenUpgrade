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
Read data from Open Object model.

Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>)
GNU General Public License
"""

from etl.component import component

class openobject_in(component):
    """
    This is an ETL Component that use to read data from open object model.
    Type: Data Component
    Computing Performance: Streamline
    Input Flows: 0
    * .* : nothing
    Output Flows: 0-x
    * .* : return the main flow with data from open object model
    """

    def __init__(self, openobject_connector, model, domain=[], fields=[], context={}, name='component.input.openerp_in', transformer=None, row_limit=0):
        """
        Required Parameters ::
        openobject_connector : Object of Openobject connector.
        model                : Name of Open Object model.
        domain               : Domain List to put domain.
        fields               : Fields List.
        context              : Context Values.

        Extra Parameters ::
        row_limit            : Row Limit.If row limit is 0,all records are fetch.
        name                 : Name of Component.
        transformer          : Transformer object to transform string data into particular type.
        """
        super(openobject_in, self).__init__(name=name, connector=openobject_connector, transformer=transformer,row_limit=row_limit)
        self._type='component.input.openerp_in'
        self.model=model
        self.domain=domain
        self.context=context
        self.fields=fields

    def __copy__(self):
        res=openobject_in(self.connector, self.model, self.domain, self.fields, self.context, self.name, self.transformer, self.row_limit)
        return res

    def process(self):
        import socket
        import xmlrpclib
        import datetime
        rows=[]
        connector=self.connector.open()
        ids = self.connector.execute(connector, 'execute', self.model, 'search', self.domain, 0, self.row_limit, False, self.context, False)
        rows = self.connector.execute(connector, 'execute', self.model, 'read', ids, self.fields, self.context)
        self.connector.close(connector)
        for row in rows:
            if row:
                yield row, 'main'

def test():
    from etl_test import etl_test
    import etl
    file_conn=etl.connector.openobject_connector('http://localhost:8069', 'trunk', 'admin','admin', con_type='xmlrpc')
    test=etl_test.etl_component_test(openobject_in(file_conn, 'res.country',[('name','=','Algeria')]))
#    test.check_input({'main':[{'name':'Elec Import'}]})
    test.check_output([{'name':'Algeria', 'code':'DZ', 'id':61}], 'main') # to be update
    res=test.output()
    print res
if __name__ == '__main__':
    test()

