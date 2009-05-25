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


class gdoc_out(component):
    """
    This is an ETL Component that writes data to facebook.
    """

    def __init__(self, gdoc_connector, method, path, name='component.input.gdoc_out', transformer=None, row_limit=0):
        super(gdoc_out, self).__init__(name=name, connector=gdoc_connector, transformer=transformer, row_limit=row_limit)
        self._type = 'component.output.gdoc_out'
        self.method = method
        self.path = path

    def __copy__(self):
        res = gdoc_out(self.connector, self.method, self.path, self.name, self.transformer, self.row_limit)
        return res

    def __getstate__(self):
        res = super(gdoc_out, self).__getstate__()
        return res

    def __setstate__(self, state):
        super(gdoc_out, self).__setstate__(state)
        self.__dict__ = state

    def save_doc(self, gdoc_service):
        print "!!!!!!!!!!!!!!!!"
        import gdata
        import gdata.docs.service
        ms = gdata.MediaSource(file_path=self.path, content_type=gdata.docs.service.SUPPORTED_FILETYPES['png'])
        entry = gdoc_service.UploadDocument(ms, 'screenshot tinyerp')
        print 'Document now accessible online at:', entry.GetAlternateLink().href

    def process(self):
        gdoc_service = self.connector.open()
        for channel, trans in self.input_get().items():
            for iterator in trans:
                for d in iterator:
                    self.save_doc(gdoc_service)
                    yield d, 'main'

def test():
#    from etl_test import etl_test
#    import etl
#    facebook_conn = etl.connector.facebook_connector('http://facebook.com', 'modiinfo@gmail.com')
#    test = etl_test.etl_component_test(facebook_out(facebook_conn, 'set_events', name='facebook test'))
#    test.check_output([{'id': 'event2', 'name': 'mustufa'}], 'main')
#    test.check_input({'main': [{'id': 'event2', 'name': 'mustufa'}]})
#    res = test.output()


    from etl_test import etl_test
    import etl
    import getpass
    user = raw_input('Enter gmail username: ')
    password = getpass.unix_getpass("Enter your password:")
    doc_conn=etl.connector.gdoc_connector(user, password)
    out_doc = gdoc_out(doc_conn, '', 'home/tiny/Desktop/1.png')
    test = etl_test.etl_component_test(out_doc)
#    test.check_output([{'phone_numbers': [''], 'postal_addresses': [''], 'emails': [''], 'title': ''}], 'main')
    # here add the details of the contact in your gmail in the above mentioned format
    res = test.output()
    print "hooo"
    print res

if __name__ == '__main__':
    test()

