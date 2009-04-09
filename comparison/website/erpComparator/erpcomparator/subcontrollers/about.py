from turbogears import expose
from turbogears import controllers
import cherrypy

from erpcomparator import rpc
from erpcomparator import common
from erpcomparator.tinyres import TinyResource

class About(controllers.Controller, TinyResource):
    
    @expose(template="erpcomparator.subcontrollers.templates.about")
    def index(self):
        return dict()
