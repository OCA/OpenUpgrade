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
To provide connectivity with OpenERP server 

Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>).
GNU General Public License
"""
from etl.connector import connector

class openobject_connector(connector):    
    def __init__(self, uri, db, login, passwd, obj='/xmlrpc/object',con_type='xmlrpc'):
        """   
        Required Parameters ::
        uri : URI path of OpenObject server with port
        db : OpenObject Database name
        login : User name to login into OpenObject Database
        passwd : Password of the user
        Extra Parameters ::
        obj : object name
        con_type : Type of connection to OpenObject
        """
        super(openobject_connector, self).__init__()
        self.db = db
        self.user_login = login
        self.obj = obj
        self.passwd = passwd
        self.con_type=con_type
        self.uid = False
        self.uri = uri

    def open(self):
        """ 
        Opens a connection to OpenObject Database
        """ 
        import xmlrpclib
        from etl import etl_socket
        connector=False
        super(openobject_connector, self).open()
        if self.con_type=='xmlrpc':
            connector= xmlrpclib.ServerProxy(self.uri+self.obj) 
        elif self.con_type=='socket':
            connector= etl_socket.etl_socket()
            self.obj = self.obj[1:]
        else:
            raise Exception('Not Supported')        
        self.uid=self.login(self.user_login,self.passwd)
        return connector

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
    
    def login(self,uid, passwd):
        """ 
        Provides login to OpenObject Database
        """ 
        import xmlrpclib
        from etl import etl_socket    
        if self.con_type=='xmlrpc':            
            xg = xmlrpclib.ServerProxy(self.uri+'/xmlrpc/common') 
            return xg.login(self.db, uid,passwd)
        elif self.con_type=='socket':            
            xg = xmlrpclib.ServerProxy(self.uri+'/xmlrpc/common') 
            return xg.login(self.db, uid,passwd)
            raise Exception('Not Implemented')
        else:
            raise Exception('Not Supported')
  
    def execute(self,connector,method, *args):     
        import xmlrpclib
        from etl import etl_socket
        super(openobject_connector, self).execute()
        if not self.uid:
            raise Exception('Not login')        
        if self.con_type=='xmlrpc':            
            result = getattr(connector,method)(self.db,self.uid,self.passwd, *args)
            return self.__convert(result)
        elif self.con_type=='socket':            
            connector.connect(self.uri)                 
            connector.mysend((self.obj, method, self.db,self.uid,self.passwd)+args)
            res = connector.myreceive()  
            connector.disconnect()       
            return res
        else:
            raise Exception('Not Supported') 

    def close(self,connector):
        """ 
        Closes the connection to OpenObject Database
        """ 
        super(openobject_connector, self).close(connector)
        return True#connector.close()
    
    def __copy__(self): 
        """
        Overrides copy method
        """
        res=openobject_connector(self.uri, self.db, self.login, self.passwd, self.obj,self.con_type) 
        res.uid=self.uid 
        return res

def test():    
    #TODO
    pass

if __name__ == '__main__':
    test()
