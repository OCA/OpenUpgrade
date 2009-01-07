
from turbogears import expose
from turbogears import controllers

from erpcomparator import rpc
from erpcomparator import tools
from erpcomparator import common

class Login(controllers.Controller):
    
    @expose(template="erpcomparator.subcontrollers.templates.login")
    def index(self, **kw):
        return dict()