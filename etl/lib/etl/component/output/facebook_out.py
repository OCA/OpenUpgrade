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
This is an ETL Component that use to write data into facebook.
"""

from etl.component import component
import time

class facebook_out(component):
    """
    # To do: to make comment here..
    """

    def __init__(self,facebook_connector,method,domain=[],fields=['name'],name='component.input.facebook_out',transformer=None,row_limit=0):
        super(facebook_out, self).__init__(name,transformer=transformer)
        self.facebook_connector = facebook_connector
        self.method=method
        self.domain=domain
        self.fields=fields
        self.row_limit=row_limit # to be check

    def process(self): 
        for channel,trans in self.input_get().items():
            for iterator in trans:
                for d in iterator:  
                    try:
                        if self.transformer:
                            d=self.transformer.transform(d)
                        connector=self.facebook_connector.open()
                        self.facebook_connector.execute(connector,self.method,fields=self.fields)
                        self.facebook_connector.close(connector)
                        yield d, 'main'
                    except Exception,e:
                        yield {'data':d,'type':'exception','message':str(e)}, 'error'         


def test():
    pass

if __name__ == '__main__':
    pass

