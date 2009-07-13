

"""
This module provides wrappers arround xmlrpclib that allows accessing
Tiny resources in pythonic way.
"""

import time
import socket
import xmlrpclib

import tiny_socket
import common

class RPCException(Exception):
           
    def __init__(self, code, backtrace):

        self.code = code
        self.args = backtrace
        if hasattr(code, 'split'):
            lines = code.split('\n')

            self.type = lines[0].split(' -- ')[0]
            self.message = ''
            if len(lines[0].split(' -- ')) > 1:
                self.message = lines[0].split(' -- ')[1]

            self.data = '\n'.join(lines[2:])
        else:
            self.type = 'error'
            self.message = backtrace
            self.data = backtrace

        self.backtrace = backtrace

    def __str__(self):
        return self.message

class RPCGateway(object):
    """Gateway abstraction, that implement common stuffs for rpc gateways.
    All RPC gateway should extends this class.
    """

    def __init__(self, host, port, protocol):

        self.protocol = protocol
        self.host = host
        self.port = port

    def _get_db(self):
        return session.db

    def _get_uid(self):
        return session.uid

    def _get_password(self):
        return session.password

    db = property(_get_db)
    uid = property(_get_uid)
    password = property(_get_password)

    def get_url(self):
        """Get the url
        """

        return "%s://%s:%s/"%(self.protocol, self.host, self.port)

    def listdb(self):
        """Get the list of databases.
        """
        pass

    def login(self, db, user, password):
        """Do login.

        @param db: the database
        @param user: the user
        @param password: the password

        @return: 1 on success else negative error value
        """
        pass

    def execute(self, obj, method, *args):
        """Excecute the method of the obj with the given arguments.

        @param obj: the object
        @param method: the method to execute
        @param args: the arguments

        @return: the result of the method
        """
        pass

    def execute_noauth(self, obj, method, *args):
        """Excecute the method of the obj with the given arguments without authentication.

        @param obj: the object
        @param method: the method to execute
        @param args: the arguments

        @return: the result of the method
        """
        pass

    def execute_db(self, method, *args):
        """Execute a database related method.
        """
        pass

class XMLRPCGateway(RPCGateway):
    """XMLRPC implementation.
    """

    def __init__(self, host, port, protocol='http'):
        """Create new instance of XMLRPCGateway.

        @param host: the host
        @param port: the port
        @param protocol: either http or https
        """
        super(XMLRPCGateway, self).__init__(host, port, protocol)
        self.url =  self.get_url() + 'xmlrpc/'

    def listdb(self):
        sock = xmlrpclib.ServerProxy(self.url + 'db')
        try:
            return sock.list()
        except Exception, e:
            return -1

    def login(self, db, user, password):
        sock = xmlrpclib.ServerProxy(self.url + 'common')
        try:
            res = sock.login(db, user, password)
        except Exception, e:
            return -1

        return res

    def _execute(self, obj, method, args=(), noauth=False):
        sock = xmlrpclib.ServerProxy(self.url + str(obj))
        try:
            if not noauth:
                args = (self.db, self.uid, self.password) + args
            return getattr(sock, method)(*args)
        except xmlrpclib.Fault, err:
            raise RPCException(err.faultCode, err.faultString)

    def execute(self, obj, method, *args):
        return self._execute(obj, method, args)

    def execute_noauth(self, obj, method, *args):
        return self._execute(obj, method, args, noauth=True)

    def execute_db(self, method, *args):
        sock = xmlrpclib.ServerProxy(self.url + 'db')
        return getattr(sock, method)(*args)

class NETRPCGateway(RPCGateway):
    """NETRPC Implementation.
    """

    def __init__(self, host, port):
        super(NETRPCGateway, self).__init__(host, port, 'socket')

    def listdb(self):
        sock = tiny_socket.mysocket()
        try:
            sock.connect(self.host, self.port)
            sock.mysend(('db', 'list'))
            res = sock.myreceive()
            sock.disconnect()
            return res
        except Exception, e:
            return -1

    def login(self, db, user, password):
        sock = tiny_socket.mysocket()
        try:
            sock.connect(self.host, self.port)
            sock.mysend(('common', 'login', db, user, password))
            res = sock.myreceive()
            sock.disconnect()
        except Exception, e:
            return -1

        return res

    def _execute(self, obj, method, args=(), noauth=False):
        sock = tiny_socket.mysocket()
        try:
            sock.connect(self.host, self.port)
            if not noauth:
                args = (self.db, self.uid, self.password) + args
            sock.mysend((obj, method) + args)
            res = sock.myreceive()
            sock.disconnect()
            return res

        except xmlrpclib.Fault, err:
            raise RPCException(err.faultCode, err.faultString)
        
        except tiny_socket.Myexception, err:
            raise RPCException(err.faultCode, err.faultString)

    def execute(self, obj, method, *args):
        return self._execute(obj, method, args)

    def execute_noauth(self, obj, method, *args):
        return self._execute(obj, method, args, noauth=True)

    def execute_db(self, method, *args):
        sock = tiny_socket.mysocket()
        sock.connect(self.host, self.port)
        sock.mysend(('db', method) + args)
        res = sock.myreceive()
        sock.disconnect()
        return res

# XXX: Fix openerp server to return PyTZ compatible timezone name
_TZ_ALIASES = {
    'IST' : 'Asia/Calcutta'
}

class RPCSession(object):
    """This is a wrapper class that provides Pythonic way to handle RPC (remote procedure call).
    It also provides a way to store session data into different kind of storage.
    """

    __slots__ = ['host', 'port', 'protocol', 'storage', 'gateway']

    def __init__(self, host, port, protocol='socket', storage={}):
        """Create new instance of RPCSession.

        @param host: the openerp-server host
        @params port: the openerp-server port
        @params protocol: the openerp-server protocol
        @param storage: a dict like storage that will be used to store session data
        """
        self.host = host
        self.port = port
        self.protocol = protocol
        self.storage = storage

        if protocol == 'http':
            self.gateway = XMLRPCGateway(host, port, 'http')
        
        elif protocol == 'https':
            self.gateway = XMLRPCGateway(host, port, 'https')

        elif protocol == 'socket':
            self.gateway = NETRPCGateway(host, port)

        else:
            raise common.message(_("Connection refused!"))

    def __getattr__(self, name):
        try:
            return super(RPCSession, self).__getattribute__(name)
        except:
            pass

        return self.storage.get(name)

    def __setattr__(self, name, value):
        if name in self.__slots__:
            super(RPCSession, self).__setattr__(name, value)
        else:
            self.storage[name] = value

    def __getitem__(self, name):
        return self.storage.get(name)

    def __setitem__(self, name, value):
        self.storage[name] = value

    def __delitem__(self, name):
        try:
            del self.storage[name]
        except:
            pass

    def get(self, name, default=None):
        return self.storage.get(name, default)

    def get_url(self):
        return self.gateway.get_url()

    def listdb(self):
        return self.gateway.listdb()

    def login(self, db, user, password):

        if password is None:
            return -1

        uid = self.gateway.login(db, user or '', password or '')

        if uid <= 0:
            return -1

        self.uid = uid
        self.db = db
        self.password = password
        self.open = True

        # read the full name of the user
        self.user_name = self.execute('object', 'execute', 'res.users', 'read', [uid], ['name'])[0]['name']

        # set the context
        self.context_reload()

        return uid

    def logout(self):
        try:
            self.storage.clear()
        except Exception, e:
            pass

    def is_logged(self):
        return self.uid and self.open

    def context_reload(self):
        """Reload the context for the current user
        """

        self.context = {'client': 'web'}
        self.timezone = 'utc'

        # self.uid
        context = self.execute('object', 'execute', 'res.users', 'context_get')
        self.context.update(context or {})
        
        if self.context.get('tz', False):
            self.timezone = self.execute('common', 'timezone_get')
            try:
                import pytz
            except:
                raise common.warning(_('You select a timezone but OpenERP could not find pytz library!\nThe timezone functionality will be disable.'))
                
        # set locale in session
        self.locale = self.context.get('lang')

    def __convert(self, result):

        if isinstance(result, basestring):
            # try to convert into unicode string
            try:
                return ustr(result)
            except Exception, e:
                return result

        elif isinstance(result, list):
            return [self.__convert(val) for val in result]

        elif isinstance(result, tuple):
            return tuple([self.__convert(val) for val in result])

        elif isinstance(result, dict):
            newres = {}
            for key, val in result.items():
                newres[key] = self.__convert(val)

            return newres

        else:
            return result

    def execute(self, obj, method, *args):

        if not self.is_logged():
            raise common.warning(_('Not logged...'), _('Authorization Error!'))

        try:
            
            #print "TERP-CALLING:", obj, method, args
            result = self.gateway.execute(obj, method, *args)
            #print "TERP-RESULT:", result
            return self.__convert(result)

        except socket.error, (e1, e2):
            raise common.message(_('Connection refused!'))

        except RPCException, err:

            if err.type in ('warning', 'UserError'):
                raise common.warning(err.data)
            else:
                raise common.error(_('Application Error!'), err.backtrace)
            
        except Exception, e:
            raise common.error(_('Application Error!'), str(e))

    def execute_noauth(self, obj, method, *args):
        return self.gateway.execute_noauth(obj, method, *args)

    def execute_db(self, method, *args):
        return self.gateway.execute_db(method, *args)

# Client must initialise session with storage.
# for example: session = RPCSession('localhost', 8070, 'socket', storage=dict())
session = None

class RPCProxy(object):
    """A wrapper arround xmlrpclib, provides pythonic way to access tiny resources.

    For example,

    >>> users = RPCProxy("ir.users")
    >>> res = users.read([1], ['name', 'active_id'], session.context)
    """

    def __init__(self, resource):
        """Create new instance of RPCProxy for the give tiny resource

        @param resource: the tinyresource
        """
        self.resource = resource
        self.__attrs = {}

    def __getattr__(self, name):
        if not name in self.__attrs:
            self.__attrs[name] = RPCFunction(self.resource, name)
        return self.__attrs[name]

class RPCFunction(object):
    """A wrapper arround xmlrpclib, provides pythonic way to execute tiny methods.
    """

    def __init__(self, object, func_name):
        """Create a new instance of RPCFunction.

        @param object: name of a tiny object
        @param func_name: name of the function
        """
        self.object = object
        self.func = func_name

    def __call__(self, *args):
        return session.execute("object", "execute", self.object, self.func, *args)

if __name__=="__main__":

    host = 'localhost'
    port = '8070'
    protocol = 'socket'

    session = RPCSession(host, port, protocol, storage=dict())

    res = session.listdb()
    print res

    res = session.login('test421', 'admin', 'admin')
    print res

    res = RPCProxy('res.users').read([session.uid], ['name'])
    print res

    res = RPCProxy('ir.values').get('action', 'tree_but_open', [('ir.ui.menu', 73)], False, {})
    print res

# vim: ts=4 sts=4 sw=4 si et

