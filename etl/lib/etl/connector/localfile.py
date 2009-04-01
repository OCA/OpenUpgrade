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
 To provide connection with local file

 Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>). 
 GNU General Public License
"""
from etl.connector import connector

class localfile(connector):
    def __init__(self,uri,bufsize=-1,encoding='utf-8'):
        """ 
        Parameters ::
        uri     :specifies path of localfile
        bufsize	:specifies buffer size in file object which is used as a connector
        encoding:provide encoding method to read/write file

        """
    
        super(localfile, self).__init__()
        self.bufsize=bufsize
        self.encoding=encoding
        self.uri = uri

    def open(self, mode='r'):
        # TODO : pass encoding in file
        super(localfile, self).open()
        self.connector=file(self.uri, mode)
        #self.file.encoding=self.encoding
        return self.connector

    def close(self):
        super(localfile, self).close()
        self.connector.close()
