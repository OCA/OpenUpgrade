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
* Open Object connector
"""
import xmlrpclib
from etl import etl_socket
from etl.connector import connector


class openobject_connector(connector.connector):    
    def __init__(self, url, db, uid, passwd, obj='/object',con_type='xmlrpc'):
        super(openobject_connector, self).__init__(uri)        
        self.db = db
        self.uid = uid
        self.obj = obj
        self.passwd = passwd
        self.con_type=con_type
        

    def open(self):
        super(openobject_connector, self).open()
        if self.con_type=='xmlrpc':
            self.connector= xmlrpclib.ServerProxy(url+obj) 
        elif self.con_type=='socket':
            self.connector= etl_socket.etl_socket()
            self.obj = obj[1:]
        else:
            raise Exception('Not Supported') 
        return self.connector

    def __convert(self, result):
        if type(result)==type(u''):
            return result.encode('utf-8')
        elif type(result)==type([]):
            return map(self.__convert, result)
        elif type(result)==type({}):
            newres = {}
            for i in result.keys():
                newres[i] = self.__convert(result[i])
            return newres
        else:
            return result 
      
    def execute(self,method, *args):
        super(openobject_connector, self).execute()
        if self.con_type=='xmlrpc':
            result = getattr(self.connector,method)(self.db, *args)
            return self.__convert(result)
        elif self.con_type=='socket':
            self.connector.connect(self.url)     
            self.connector.mysend((self.obj, method, self.db)+args)
            res = self.connector.myreceive()  
            self.connector.disconnect()       
            return res
        else:
            raise Exception('Not Supported') 
