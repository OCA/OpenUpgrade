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
 To provide connectivity with OpenERP server.

 Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>).
 GNU General Public License.
"""
from etl.connector import connector

class openobject_connector(connector):
    """
    This is an ETL connector that is used to provide connectivity with OpenERP server.
    """
    def __init__(self, uri, db, login, passwd, obj='/xmlrpc/object', con_type='xmlrpc', name='openobject_connector'):
        """
        Required Parameters
        uri    : URI path of OpenObject server with port.
        db     : OpenObject Database name.
        login  : User name to login into OpenObject Database.
        passwd : Password of the user.

        Extra Parameters
        obj      : Object name.
        con_type : Type of connection to OpenObject.
        """
        super(openobject_connector, self).__init__(name)
        self._type = 'connector.openobject_connector'
        self.db = db
        self.user_login = login
        self.obj = obj
        self.passwd = passwd
        self.con_type = con_type
        self.uid = False
        self.uri = uri

    def open(self):
        """
        Opens a connection to OpenObject Database.
        """
        import xmlrpclib
        from etl import etl_socket
        connector = False
        super(openobject_connector, self).open()
        if self.con_type == 'xmlrpc':
            connector = xmlrpclib.ServerProxy(self.uri + self.obj)
        elif self.con_type == 'socket':
            connector = etl_socket.etl_socket()
#            self.obj = self.obj[1:]
        else:
            raise Exception('Not Supported')
        self.uid = self.login(self.user_login, self.passwd)
        return connector

    def __getstate__(self):
        res = super(openobject_connector, self).__getstate__()
        res.update({'db':self.db, 'user_login':self.user_login, 'obj':self.obj, 'passwd':self.passwd, 'con_type':self.con_type, 'uid':self.uid, 'uri':self.uri})
        return res

    def __setstate__(self, state):
        super(openobject_connector, self).__setstate__(state)
        self.__dict__ = state

    def __convert(self, result):
        if type(result) == type(u''):
            return result.encode('utf-8')
        elif type(result) == type([]):
            return map(self.__convert, result)
        elif type(result) == type({}):
            newres = {}
            for i in result.keys():
                newres[i] = self.__convert(result[i])
            return newres
        else:
            return result

    def login(self, uid, passwd):
        """
        For logging in to OpenObject Database.
        """
        import xmlrpclib
        from etl import etl_socket
        if self.con_type == 'xmlrpc':
            xg = xmlrpclib.ServerProxy(self.uri + '/xmlrpc/common')
            return xg.login(self.db, uid,passwd)
        elif self.con_type == 'socket':
            connector = etl_socket.etl_socket()
            connector.connect(self.uri)
            connector.mysend(('common', 'login', self.db or '', uid or '', passwd or ''))
            res = connector.myreceive()
            connector.disconnect()
            return res
        else:
            raise Exception('Not Supported')

    def execute(self,connector, method, *args):
        import xmlrpclib
        from etl import etl_socket
        super(openobject_connector, self).execute()
        if not self.uid:
            raise Exception('Not login')
        if self.con_type == 'xmlrpc':
            result = getattr(connector, method)(self.db, self.uid, self.passwd, *args)
            return self.__convert(result)
        elif self.con_type == 'socket':
            connector = etl_socket.etl_socket()
            connector.connect(self.uri)
            connector.mysend((self.obj, method, self.db, self.uid, self.passwd) + args)
            res = connector.myreceive()
            connector.disconnect()
            return res
        else:
            raise Exception('Not Supported')

    def close(self, connector):
        """
        Closes the connection made to OpenObject Database.
        """
        super(openobject_connector, self).close(connector)
        return True#connector.close()

    def __copy__(self):
        res = openobject_connector(self.uri, self.db, self.login, self.passwd, self.obj, self.con_type, self.name)
        res.uid = self.uid
        return res

def test():
    from etl_test import etl_test
    import etl
    openobject_partner=openobject_connector('http://localhost:8070', 'trunk', 'admin', 'a', obj='object', con_type='socket')
    test = etl_test.etl_component_test(etl.component.input.openobject_in(
                 openobject_partner,'res.partner.address',
                 fields=['partner_id','title', 'name', 'street', 'street2' , 'phone' , 'city' ,  'zip' ,'state_id' , 'country_id' , 'mobile', 'birthdate'],
))
    res=test.output()
    print res
    #TODO

if __name__ == '__main__':
    test()
