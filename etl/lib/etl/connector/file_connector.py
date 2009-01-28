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
ETL Connectors:
* File Access
"""
from etl import etl

class file_connector(etl.connector):
    def __init__(self,host,port,uid,pwd,connection_type,path,*args, **argv):
        super(file_connector, self).__init__(*args, **argv)
        self.connection_type=connection_type
        self.path=path      
        self.connection_string=connection_type+'://'+uid+':'+pwd+'@'+host+':'+port+'/'+path  
        self.file=False
    def __init__(self,connection_string,*args, **argv):
        super(file_connector, self).__init__(*args, **argv)
        self.connection_string=connection_string
    def open(self,mode='r',bufsize=-1,encoding='utf-8'):
        super(file_connector, self).open(mode)
        self.file=open(self.connection_string,mode,bufsize)    
        #self.file.encoding=encoding
        return self.file
    def close(self):
        super(file_connector, self).close()
        self.file.close()    
