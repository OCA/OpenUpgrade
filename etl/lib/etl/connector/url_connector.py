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
 To provide connectivity with URL Access like  http, ftp, https, gopher

 Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>).
 GNU General Public License.
"""
from etl.connector import connector
import urllib

class url_connector(connector):
    """
    This is an ETL connector that is used to provide connectivity URL Access like  http, ftp, https, gopher.
    """
    def __init__(self, uri, bufsize=-1, encoding='utf-8', name='url_connector'):
        """
        Required Parameters
        uri      : Path of file.

        Extra Parameters
        bufsize  : Buffer size for reading data.
        encoding : Encoding format.
        name     : Name of connector.
        """
        super(url_connector, self).__init__(name)
        self._type = 'connector.url_connector'
        self.bufsize = bufsize
        self.encoding = encoding
        self.uri = uri

    def __getstate__(self):
        res = super(url_connector, self).__getstate__()
        res.update({'bufsize':self.bufsize, 'encoding':self.encoding, 'uri':self.uri})
        return res

    def __setstate__(self, state):
        super(url_connector, self).__setstate__(state)
        self.__dict__ = state

    def open(self):
        """
        Opens the specified URL.
        """
        # TODO : pass encoding in file
        super(url_connector, self).open()
        connector = urllib.URLopener().open(self.uri)
        #self.file.encoding = self.encoding
        return connector

    def close(self):
        super(url_connector, self).close()
        connector.close()

    def __copy__(self):
        res = url_connector(self.uri, self.bufsize, self.encoding, self.name)
        return res

