from turbogears import expose
from turbogears import controllers
import cherrypy

from erpcomparator import rpc
from erpcomparator import common

class News(controllers.Controller):
    
    @expose(template="erpcomparator.subcontrollers.templates.news")
    def index(self):
        userinfo = cherrypy.session.get('user_info', '')
        
        return dict(mess = "under progress...")