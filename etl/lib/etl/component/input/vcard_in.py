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
 To import data from vcard.

 Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>).
 GNU General Public License.
"""

from etl.component import component

class vcard_in(component):

    def __init__(self,fileconnector, name='component.input.csv_in', transformer=None, row_limit=0):
    	"""
    	Required Parameters
    	fileconnector : Local file connector to connect with file.

        Extra Parameters
        name          : Name of Component.
        """
        super(vcard_in, self).__init__(name=name, connector=fileconnector, transformer=transformer, row_limit=row_limit)
        self._type = 'component.input.vcard_in'

    def __copy__(self):
        res = vcard_in(self.connector, self.name, self.transformer, self.row_limit)
        return res

    def end(self):
        super(vcard_in, self).end()
        if self.fp:
            self.connector.close(self.fp)
            self.fp = False

    def __getstate__(self):
        res = super(vcard_in, self).__getstate__()
        return res

    def __setstate__(self, state):
        super(vcard_in, self).__setstate__(state)
        self.__dict__ = state

    def process(self):
        import vobject
        self.fp = self.connector.open('r')
        s = "".join(self.fp.readlines())
        reader = vobject.readComponents(s)
        while True:
            row = {}
            data = reader.next()
            for d in data.contents:
                row[unicode(d)] = eval('data.' + unicode(d) + '.value')
            yield row, 'main'

def test():
    from etl_test import etl_test
    import etl
    file_conn = etl.connector.localfile('../../../demo/input/input1.vcf')
    test = etl_test.etl_component_test(vcard_in(file_conn, name='vcf test'))
    test.check_output([{u'tel': u'(111) 555-1212', u'title': u'Shrimp Man', u'rev': u'20080424T195243Z', u'version': u'3.0', u'org': [u'BubbaGumpShrimp'], u'label': u'100 Waters Edge\\nBaytown, LA 30314\\nUnited States of America', u'email': u'forrestgump@example.com', u'fn': u'ForrestGump'}], 'main')
    res = test.output()
    print res

if __name__ == '__main__':
    test()
