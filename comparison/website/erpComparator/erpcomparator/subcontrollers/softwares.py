from turbogears import expose
from turbogears import controllers
import cherrypy

from erpcomparator import rpc
from erpcomparator import common
from erpcomparator.tinyres import TinyResource

class Softwares(controllers.Controller, TinyResource):
    
    @expose(template="erpcomparator.subcontrollers.templates.softwares")
    def index(self):
        proxy = rpc.RPCProxy('comparison.item')
        
        ids = proxy.search([])        
        res = proxy.read(ids, ['name', 'note'])
            
        return dict(res=res)
