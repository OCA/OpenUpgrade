
from turbogears import expose, redirect
from turbogears import controllers
import cherrypy

from erpcomparator import rpc
from erpcomparator import tools
from erpcomparator import common

class Login(controllers.Controller):
    
    @expose(template="erpcomparator.subcontrollers.templates.login")
    def index(self):
        
        userinfo = cherrypy.session.get('user_info', '')
        message = None
        user_name = None
        password = None
        
        return dict(message=message, userinfo=userinfo)
    
    @expose(template="erpcomparator.subcontrollers.templates.login")
    def do_login(self, **kw):
        
        userinfo = None
        message = None
        user_name = kw.get('user')
        password = kw.get('password')
        
        model = 'comparison.user'
        
        proxy = rpc.RPCProxy(model)
        ids = proxy.search([])
        res = proxy.read(ids, ['name', 'password'])
        
        for r in res:
            if r['name'] == user_name and r['password'] == password:
                login_info = {}
                login_info['name'] = user_name
                login_info['password'] = password
                
                cherrypy.session['login_info'] = login_info
        
        if cherrypy.session.get('login_info'):
            raise redirect('/index/')
        else:
            message = "Username or password is invalid."
            return dict(userinfo=userinfo, message=message)
    
    @expose(template="erpcomparator.templates.index")
    def logout(self):
        if cherrypy.session.get('login_info'):
            cherrypy.session['login_info'] = None
            
        return dict()
    
    
    