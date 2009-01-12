from turbogears import expose
from turbogears import controllers
import cherrypy

from erpcomparator import rpc
from erpcomparator import common

class About(controllers.Controller):
    
    @expose(template="erpcomparator.subcontrollers.templates.about")
    def index(self):
        msg = "This is About....."
        
        userinfo = cherrypy.session.get('user_info', '')
        
        return dict(msg=msg, userinfo=userinfo)
