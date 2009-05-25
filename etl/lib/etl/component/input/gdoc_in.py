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

from etl.component import component

class gdoc_in(component):

    def __init__(self, gdoc_conn, file_path, name='component.input.gdoc_in', transformer=None, row_limit=0):
        """
        Required  Parameters
        gdoc_conn     : connector for google doc

        Extra Parameters
        name          : Name of Component.
        row_limit     : Limited records are sent to destination if row limit is specified. If row limit is 0, all records are sent.
        """
        super(gdoc_in, self).__init__(connector=gdoc_conn, name=name, transformer=transformer, row_limit=row_limit)
        self._type = 'component.input.gdoc_in'
        self.file_path = file_path

    def __copy__(self):
        res = gdoc_in(self.gdoc_conn, self.name, self.transformer, self.row_limit)
        return res

    def __getstate__(self):
        res = super(gdoc_in, self).__getstate__()
        return res

    def __setstate__(self, state):
        super(gdoc_in, self).__setstate__(state)
        self.__dict__ = state

    def process(self):
        import gdata.docs.service
        gdoc_service = self.connector.open()
        documents_feed = gdoc_service.GetDocumentListFeed()
        for document_entry in documents_feed.entry:
            gdoc_service.DownloadDocument(document_entry, self.file_path)
            yield {}, 'main'

def test():
    from etl_test import etl_test
    import etl
    import getpass
    user = raw_input('Enter gmail username: ')
    password = getpass.unix_getpass("Enter your password:")
    doc_conn=etl.connector.gdoc_connector('mustufa.2007','zainabrupawala')
    in_doc = gdoc_in(doc_conn, 'home/tiny/Desktop/doc1.doc')
    test = etl_test.etl_component_test(in_doc)
#    test.check_output([{'phone_numbers': [''], 'postal_addresses': [''], 'emails': [''], 'title': ''}], 'main')
    # here add the details of the contact in your gmail in the above mentioned format
    res = test.output()
    print "hooo"

if __name__ == '__main__':
    test()

#
#>>> #
#... import urllib2
#>>> import urllib2
#>>> opener1 = urllib2.build_opener()
#>>> page1 = opener1.open("http://docs.google.com/gb?export=download&id=F.83ab449a-e9d9-4517-bce9-0473c0a9f5c3")
#>>> my_picture = page1.read()
#>>> filename = "my_image" + picture_page[-4:]
#Traceback (most recent call last):
#  File "<stdin>", line 1, in <module>
#NameError: name 'picture_page' is not defined
#>>> filename = "my_image"
#>>> fout = open('/home/tiny/Desktop/filename, "wb")
#  File "<stdin>", line 1
#    fout = open('/home/tiny/Desktop/filename, "wb")
#                                                  ^
#SyntaxError: EOL while scanning single-quoted string
#>>> fout = open('/home/tiny/Desktop/filename', "wb")
#>>> fout.write(my_picture)
#>>> fout.write(my_picture)
#>>> fout = open('/home/tiny/Desktop/filename', "wb")
#>>> fout.write(my_picture)
#>>>


