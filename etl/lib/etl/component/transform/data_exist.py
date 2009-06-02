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
 To perform unique operation.

 Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>).
 GNU General Public License.
"""

from etl.component import component
class data_exist(component):
    """
        This is an ETL Component that connects on an OpenERP server and check the existancy of incoming data into the OpenERP server.

    """

    def __init__(self, openobject_injector, key, name='component.transform.data_exist'):
        super(data_exist, self).__init__(name=name )
        self._type = 'component.transfer.data_exist'
        self.openobject_injector = openobject_injector
        self.conn = self.openobject_injector.connector.open()
        self.key = key

    def __getstate__(self):
        res = super(data_exist, self).__getstate__()
        # to do: update res dic by connector and key
        return res

    def __setstate__(self, state):
        super(data_exist, self).__setstate__(state)
        self.__dict__ = state


    def process(self):
        #process incoming data
        for channel, trans in self.input_get().items():
            for iterator in trans:
                for d in iterator:
                    #check if record exists on openobject_injector
                    ids = self.openobject_injector.connector.execute(self.conn, 'execute', self.openobject_injector.model, 'search', [(self.key,'=',d[self.key])], 0, self.openobject_injector.row_limit, False, self.openobject_injector.context, False)
                    if ids:
                        yield d, 'duplicated'
                    else :
                        yield d, 'main'
        self.openobject_injector.connector.close(self.conn)


#TODO unique test
