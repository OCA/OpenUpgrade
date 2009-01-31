from turbogears import expose
from turbogears import controllers
import cherrypy

from erpcomparator import rpc
from erpcomparator import common

class Document(controllers.Controller):
    
    @expose(template="erpcomparator.subcontrollers.templates.document")
    def index(self):
        userinfo = cherrypy.session.get('user_info', '')
        
        return dict(mess = "under progress...")