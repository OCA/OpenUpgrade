from turbogears import expose
from turbogears import controllers
import cherrypy
import re

import os 
 
from erpcomparator import rpc
from erpcomparator import common
from erpcomparator.tinyres import TinyResource

class Softwares(controllers.Controller, TinyResource):
    
    @expose(template="erpcomparator.subcontrollers.templates.softwares")
    def index(self):
        proxy = rpc.RPCProxy('comparison.item')
        url_re = re.compile('(http\:\/\/[^\s]+)|(file\:\/\/[^\s]+)|(ftp\:\/\/[^\s]+)|(https\:\/\/[^\s]+)', re.MULTILINE)
        ids = proxy.search([], 0, 0, 0, rpc.session.context)        
        res = proxy.read(ids, ['name', 'note', 'code'], rpc.session.context)
        
        full_dir = os.path.realpath("erpcomparator/static/images/Screenshots")
        lst_folder = os.listdir(full_dir)    
          
        for note in res:
            files = []
            file_names = [] 
            
            if note['note']:
                notes = str(note['note'])
                note['note'] = re.sub(r'<','less than',notes) or re.sub(r'>', 'greater than', notes)
                def substitue_url(a):
                    url = a.group(0)
                    return "<a href='%s'>%s</a>" % (url, url)
                note['note'] = url_re.sub(substitue_url, note['note'])
                note['note'] = note['note'].replace('\n',' <br/>')
                note['note'] = note['note'].replace('&','&amp;')
                
            for d in lst_folder: 
                key = d.split("_")[0]
                if key == note['code']:
                    files.append(d)
                    lst = d.split('_')[1].split('.')[0]
                    file_names.append(lst)
            
            note['code'] = {note['code']: [files, file_names]}

        return dict(res=res)
