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
This is an ETL Component that writes data to google doc.
"""

from etl.component import component


class gdoc_out(component):
    """
    This is an ETL Component that writes data to google doc.
    """

    def __init__(self, gdoc_connector, method, path, doc_type='DOC', title='Document', name='component.output.gdoc_out', transformer=None, row_limit=0):
        super(gdoc_out, self).__init__(name=name, connector=gdoc_connector, transformer=transformer, row_limit=row_limit)
        self._type = 'component.output.gdoc_out'
        self.method = method
        self.path = path
        self.doc_type = doc_type
        self.title = title

    def __copy__(self):
        res = gdoc_out(self.connector, self.method, self.path, self.doc_type , self.title, self.name, self.transformer, self.row_limit)
        return res

    def __getstate__(self):
        res = super(gdoc_out, self).__getstate__()
        return res

    def __setstate__(self, state):
        super(gdoc_out, self).__setstate__(state)
        self.__dict__ = state

    def upload_doc(self, gdoc_service):
        # Todo: check by uploading different file types
        #       check for upload document to a folder
        #       create new document (blank) on google
        #       modify exiting doucment and its metadata
        #       check for permission on docs
        #       retrieve doc/ppt/ss by query...
        #       folder management
        import gdata.docs.service
        ms = gdata.MediaSource(file_path=self.path, content_type=gdata.docs.service.SUPPORTED_FILETYPES[self.doc_type])
        entry = gdoc_service.UploadDocument(ms, self.title)

    def upload_ppt(self, gdoc_service):
        import gdata.docs.service
        ms = gdata.MediaSource(file_path=self.path, content_type=gdata.docs.service.SUPPORTED_FILETYPES['PPT'])
        entry = gdoc_service.UploadPresentation(ms, self.title)

    def upload_spreadsheet(self, gdoc_service):
        import gdata.docs.service
        ms = gdata.MediaSource(file_path=self.path, content_type=gdata.docs.service.SUPPORTED_FILETYPES['XLS'])
        entry = gdoc_service.UploadSpreadsheet(ms, self.title)

    def process(self):
        gdoc_service = self.connector.open()

        if self.doc_type == 'DOC':
            self.upload_doc(gdoc_service)
        elif self.doc_type == 'PPT':
            self.upload_ppt(gdoc_service)
        elif self.doc_type == 'XLS':
            self.upload_spreadsheet(gdoc_service)

        for channel, trans in self.input_get().items():
            for iterator in trans:
                for d in iterator:
                    yield d, 'main'

def test():
    from etl_test import etl_test
    import etl
    import getpass
    user = raw_input('Enter gmail username: ')
    password = getpass.unix_getpass("Enter your password:")
    doc_conn=etl.connector.gdoc_connector(user, password)
#    out_doc = gdoc_out(doc_conn, '', '/home/tiny/Desktop/1st Review.ppt','PPT')
#    out_doc = gdoc_out(doc_conn, '', '/home/tiny/Desktop/changes.doc','DOC')
    out_doc = gdoc_out(doc_conn, '', '/home/tiny/Desktop/SDP-II group allocation.xls','XLS')
    test = etl_test.etl_component_test(out_doc)
#    test.check_output([{'phone_numbers': [''], 'postal_addresses': [''], 'emails': [''], 'title': ''}], 'main')
    res = test.output()
    print res

if __name__ == '__main__':
    test()