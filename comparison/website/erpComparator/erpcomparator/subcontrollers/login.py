
from turbogears import expose, redirect
from turbogears import controllers
import cherrypy

from erpcomparator import rpc
from erpcomparator import tools
from erpcomparator import common
from erpcomparator.tinyres import TinyResource

class Login(controllers.Controller, TinyResource):
    
    @expose(template="erpcomparator.subcontrollers.templates.login")
    def index(self):
        return dict()
   
    @expose('json')
    def do_login(self, **kw):
        
        name = kw.get('user_name')
        password = kw.get('password')
        email = kw.get('email')
        
        model = 'comparison.user'
        
        user_proxy = rpc.RPCProxy(model)
                
        res = None
        error = ''
        
        try:
            res = user_proxy.create({'name': name, 'password': password, 'email': email})
        except Exception, e:
            return dict(res=res, error=str(e))
        
        if res:
            return dict(res=res, error=error)
        
    @expose()
    def logout(self):
        cherrypy.session['login_info'] = None
        raise redirect('/comparison')
    
    
    