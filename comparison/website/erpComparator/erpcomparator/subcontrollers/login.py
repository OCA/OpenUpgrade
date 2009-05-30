
from turbogears import expose, redirect
from turbogears import controllers
import cherrypy

from erpcomparator import rpc
from erpcomparator import tools
from erpcomparator import common
from erpcomparator.tinyres import TinyResource

class Login(controllers.Controller, TinyResource):
    
    @expose(template="erpcomparator.subcontrollers.templates.login")
    def index(self, **kw):
        if kw.get('msg'):
            error = str(kw.get('msg'))
        else:
            error = ""
        return dict(error = error)
   
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
            cherrypy.session['login_info'] = name
            return dict(res=res, error=error)
    
    @expose('json')
    def check_login(self, **kw):
        
        user_name = kw.get('user_name')
        password = kw.get('password')
        
        if user_name and password:
            model = 'comparison.user'
    
            proxy = rpc.RPCProxy(model)
            uids = proxy.search([], 0, 0, 0, rpc.session.context)
            ures = proxy.read(uids, ['name', 'password'], rpc.session.context)
            
            for r in ures:
                if r['name'] == user_name and r['password'] == password:
                    login_info = {}
                    login_info['name'] = user_name
                    login_info['password'] = password
                    
                    cherrypy.session['login_info'] = user_name
                    
        user_info = cherrypy.session.get('login_info', None)
        
        if user_info:
            return dict(user_info=user_info)
        else:
            return dict(error="Username or Password invalid...")
    
    @expose()
    def logout(self):
        cherrypy.session['login_info'] = None
        raise redirect('/comparison')
    
    
    