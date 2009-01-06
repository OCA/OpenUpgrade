from turbogears import expose
from turbogears import controllers

from erpcomparator import rpc
from erpcomparator import common

class About(controllers.Controller):
    
    @expose(template="erpcomparator.subcontrollers.templates.about")
    def index(self):
        msg = "This is About....."
        return dict(msg=msg)
