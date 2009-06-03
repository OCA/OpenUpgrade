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
This is an ETL Component that writes data to blogger.
"""

from etl.component import component


class gblog_out(component):
    """
    This is an ETL Component that writes data to google blogger.
    """

    def __init__(self, gblog_connector, name='component.output.gblog_out', transformer=None, row_limit=0):
        super(gblog_out, self).__init__(name=name, connector=gblog_connector, transformer=transformer, row_limit=row_limit)
        self._type = 'component.output.gblog_out'

    def __copy__(self):
        res = gblog_out(self.connector, self.name, self.transformer, self.row_limit)
        return res

    def __getstate__(self):
        res = super(gblog_out, self).__getstate__()
        return res

    def __setstate__(self, state):
        super(gblog_out, self).__setstate__(state)
        self.__dict__ = state

    def process(self):
        from gdata import service
        import gdata
        import atom

        gblog_service = self.connector.open()
        feed = gblog_service.Get('/feeds/default/blogs')
        self_link = feed.entry[0].GetSelfLink()
        if self_link:
            blog_id = self_link.href.split('/')[-1]
        for channel, trans in self.input_get().items():
            for iterator in trans:
                for d in iterator:
                    entry = gdata.GDataEntry()
                    entry.author.append(atom.Author(atom.Name(text='uid')))
                    entry.title = atom.Title(title_type='xhtml', text=d['name'])
                    entry.content = atom.Content(content_type='html', text=d['description'])
                    gblog_service.Post(entry,
                    '/feeds/' + blog_id + '/posts/default')
                    yield d, 'main'


def test():
    # to be test
    pass

if __name__ == '__main__':
    test()