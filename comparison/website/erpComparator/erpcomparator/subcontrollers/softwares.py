from turbogears import expose
from turbogears import controllers
import cherrypy
import re

from erpcomparator import rpc
from erpcomparator import common
from erpcomparator.tinyres import TinyResource

class Softwares(controllers.Controller, TinyResource):
    
    @expose(template="erpcomparator.subcontrollers.templates.softwares")
    def index(self):
        proxy = rpc.RPCProxy('comparison.item')
        url_re = re.compile('(http\:\/\/[^\s]+)|(file\:\/\/[^\s]+)|(ftp\:\/\/[^\s]+)|(https\:\/\/[^\s]+)', re.MULTILINE)
        ids = proxy.search([])        
        res = proxy.read(ids, ['name', 'note'])
        
        for note in res:
            if note['note']:
                notes = str(note['note'])
                note['note'] = re.sub(r'<','less than',notes) or re.sub(r'>', 'greater than', notes)
                def substitue_url(a):
                    url = a.group(0)
                    return "<a href='%s'>%s</a>" % (url, url)
                note['note'] = url_re.sub(substitue_url, note['note'])
                note['note'] = note['note'].replace('\n',' <br/>')
                note['note'] = note['note'].replace('&','&amp;')
        return dict(res=res)
