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
To provide connectivity with file

 Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>). 
 GNU General Public License
"""

from etl.connector import connector

class file_connector(connector):
    """
    This is an ETL connector that use to provide connectivity with file.
    """
    def __init__(self,uri,bufsize=-1,encoding='utf-8',name='file_connector'):
        """ 
        Required Parameters ::
        uri      : Path of file
        Extra Parameters ::
        bufsize  : Bufsize for reading data
        encoding : Encoding format
        name     : Name of connector
        """    
        super(file_connector, self).__init__(name)
        self.bufsize=bufsize
        self.encoding=encoding
        self.uri = uri

    def open(self, mode='r'):
        """
        Opens file connections
        """
        super(file_connector, self).open()
        return file(self.uri, mode)        
        

    def close(self,connector):
        """
        Closes file connections
        """
        super(file_connector, self).close(connector)
        return connector.close()
    
    def __copy__(self): 
        """
        Overrides copy method
        """
        res=file_connector(self.uri,self.bufsize,self.encoding,self.name)
        return res

def test():
    file_conn=file_connector('test.txt')
    con=file_conn.open()
    file_conn.close(con)

if __name__ == '__main__':
    test()
