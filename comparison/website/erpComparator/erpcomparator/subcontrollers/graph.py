from turbogears import expose
from turbogears import controllers
import cherrypy

from erpcomparator import rpc
from erpcomparator import common

class Graph(controllers.Controller):
    
    @expose(template="erpcomparator.subcontrollers.templates.graph")
    def index(self):
        
        userinfo = cherrypy.session.get('user_info', '')
            
        return dict(mess="This is Graph.. Under Processing...")
