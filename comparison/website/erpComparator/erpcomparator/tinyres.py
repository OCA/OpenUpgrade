
"""
This modules implements custom authorization logic for the OpenERP Web Client.
"""

import time
import types
import re

from turbogears import expose
from turbogears import redirect
from turbogears import config

import cherrypy
import rpc
import pkg_resources

@expose()
def _login(target, dblist=None, db= None, user=None, action=None, message=None, origArgs={}):
    """Login page, exposed without any controller, will be used by _check_method wrapper
    """
    url = rpc.session.get_url()
    url = str(url[:-1])
    
    raise redirect('/comparison')

#    return dict(target=target, url=url, dblist=dblist, user=user, password=None, 
#            db=db, action=action, message=message, origArgs=origArgs, selected_items=[], 
#            titles=[], headers=[], url_params=[])

def secured(fn):
    """A Decorator to make a TinyResource controller method secured.
    """
    def clear_login_fields(kw={}):

        if not kw.get('login_action'):
            return

        if kw.has_key('db'): del kw['db']
        if kw.has_key('user'): del kw['user']
        if kw.has_key('password'): del kw['password']
        if kw.has_key('login_action'): del kw['login_action']

    def get_orig_args(kw={}):
        if not kw.get('login_action'):
            return kw

        new_kw = kw.copy()

        if new_kw.has_key('db'): del new_kw['db']
        if new_kw.has_key('user'): del new_kw['user']
        if new_kw.has_key('password'): del new_kw['password']
        if new_kw.has_key('login_action'): del new_kw['login_action']

        return new_kw

    def wrapper(*args, **kw):
        """The wrapper function to secure exposed methods
        """

        if rpc.session.is_logged():
            # User is logged in; allow access
            clear_login_fields(kw)
            return fn(*args, **kw)
        else:
            # User isn't logged in yet.

            db = None
            user = None
            password = None
            message = None

            action = kw.get('login_action')

            # get some settings from cookies
            try:
                db = cherrypy.request.simple_cookie['terp_db'].value
                user = cherrypy.request.simple_cookie['terp_user'].value
            except:
                pass
            
            db = config.get('database', path="admin")
            user = config.get('user_name', path="admin")
            password = config.get('password', path="admin")

            db = kw.get('db', db)
            user = kw.get('user', user)
            password = kw.get('password', password)

            # See if the user just tried to log in
            if rpc.session.login(db, user, password) <= 0:
                # Bad login attempt
                dblist = rpc.session.listdb()
                if dblist == -1:
                    dblist = []
                    message = _("Could not connect to server!")

                if action == 'login':
                    message = _("Bad username or password!")
                
                if config.get('dblist.filter', path='openerp-web'):
                    
                    headers = cherrypy.request.headers
                    host = headers.get('X-Forwarded-Host', headers.get('Host'))

                    base = re.split('\.|:|/', host)[0]                
                    base = base + '_'                
                    dblist = [d for d in dblist if d.startswith(base)]
                    
                return _login(cherrypy.request.path, message=message, dblist=dblist, db=db, 
                        user=user, action=action, origArgs=get_orig_args(kw))

            # Authorized. Set db, user name in cookies
            expiration_time = time.strftime("%a, %d-%b-%Y %H:%M:%S GMT", time.gmtime(time.time() + ( 60 * 60 * 24 * 365 )))
            cherrypy.response.simple_cookie['terp_db'] = db
            cherrypy.response.simple_cookie['terp_user'] = user.encode('utf-8')
            cherrypy.response.simple_cookie['terp_db']['expires'] = expiration_time;
            cherrypy.response.simple_cookie['terp_user']['expires'] = expiration_time;

            # User is now logged in, so show the content
            clear_login_fields(kw)
            return fn(*args, **kw)

    # restore the original values
    wrapper.__name__ = fn.__name__
    wrapper.__doc__ = fn.__doc__
    wrapper.__dict__ = fn.__dict__.copy()
    wrapper.__module__ = fn.__module__

    wrapper.secured = True

    return wrapper

def unsecured(fn):
    """A Decorator to make a TinyResource controller method unsecured.
    """

    def wrapper(*args, **kw):
        return fn(*args, **kw)

    # restore the original values
    wrapper.__name__ = fn.__name__
    wrapper.__doc__ = fn.__doc__
    wrapper.__dict__ = fn.__dict__.copy()
    wrapper.__module__ = fn.__module__

    wrapper.secured = False

    return wrapper

class TinyResource(object):
    """Provides a convenient way to secure entire TG controller
    """
    def __getattribute__( self, name ):
        value= object.__getattribute__(self, name)

        if isinstance(value, types.MethodType ) and hasattr(value, "exposed") and not (hasattr(value, "secured") and not value.secured):
            return secured(value)

        # Some other property
        return value

# vim: ts=4 sts=4 sw=4 si et

