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
This is an ETL Component that writes data to facebook.
"""

from etl.component import component


class facebook_out(component):
    """
    This is an ETL Component that writes data to facebook.
    """

    def __init__(self, facebook_connector, method, domain=[], fields=['name'], name='component.input.facebook_out', transformer=None, row_limit=0):
        super(facebook_out, self).__init__(name=name, connector=facebook_connector, transformer=transformer, row_limit=row_limit)
        self._type = 'component.output.facebook_out'
        self.method = method
        self.domain = domain
        self.fields = fields

    def __copy__(self):
        res = facebook_out(self.connector, self.name, self.transformer, self.row_limit)
        return res

    def end(self):
        super(facebook_out, self).end()
        if self.facebook:
            self.connector.close(self.facebook)
            self.facebook = False

    def __getstate__(self):
        res = super(facebook_out, self).__getstate__()
        res.update({'method':self.method, 'domain':self.domain, 'fields':self.fields})
        return res

    def __setstate__(self, state):
        super(facebook_out, self).__setstate__(state)
        self.__dict__ = state

    def process(self):
        for channel, trans in self.input_get().items():
            for iterator in trans:
                for d in iterator:
                    if not self.facebook:
                        self.facebook = self.connector.open()
                    self.connector.execute(self.facebook, self.method, fields=self.fields)
                    yield d, 'main'

def test():
    from etl_test import etl_test
    import etl
    facebook_conn = etl.connector.facebook_connector('http://facebook.com', 'modiinfo@gmail.com')
    test = etl_test.etl_component_test(facebook_out(facebook_conn, 'set_events', name='facebook test'))
    test.check_output([{'id': 'event2', 'name': 'mustufa'}], 'main')
    test.check_input({'main': [{'id': 'event2', 'name': 'mustufa'}]})
    res = test.output()
    print res

if __name__ == '__main__':
    test()

