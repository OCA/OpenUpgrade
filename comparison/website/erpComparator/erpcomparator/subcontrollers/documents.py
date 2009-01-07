from turbogears import expose
from turbogears import controllers

from erpcomparator import rpc
from erpcomparator import common

class Documents(controllers.Controller):
    
    @expose(template="erpcomparator.subcontrollers.templates.documents")
    def index(self):
        msg = "This is Documents....."
        return dict(msg=msg)
