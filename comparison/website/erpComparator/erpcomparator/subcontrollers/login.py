
from turbogears import expose, redirect
from turbogears import controllers
import cherrypy

from erpcomparator import rpc
from erpcomparator import tools
from erpcomparator import common

class Login(controllers.Controller):
    
    @expose(template="erpcomparator.subcontrollers.templates.login")
    def index(self):
        return dict()
    
    @expose()
    def do_login(self, **kw):
        name = kw.get('user_name')
        password = kw.get('password')
        email = kw.get('email')
        
        user_proxy = rpc.RPCProxy('comparison.user')
        
        res = None
        error = ''
        
        try:
            res = user_proxy.create({'name': name, 'password': password, 'email': email})
        except Exception, e:
            return dict(error=str(e))
        
        if res:
            raise redirect('/comparison?user_name=%s&password=%s' % (name, password))
        else:
            raise redirect('/comparison?error=%s' % (error))
        
    @expose()
    def logout(self):
        cherrypy.session['login_info'] = None
        raise redirect('/comparison')
    
    
    