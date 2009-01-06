from turbogears import expose
from turbogears import controllers

from erpcomparator import rpc
from erpcomparator import common

class Comparison(controllers.Controller):
    
    @expose(template="erpcomparator.subcontrollers.templates.comparison")
    def index(self):
        
        proxy = rpc.RPCProxy('comparison.factor')
        ids = proxy.search([])
        
        
        return dict(msg = "This is comparison......")
