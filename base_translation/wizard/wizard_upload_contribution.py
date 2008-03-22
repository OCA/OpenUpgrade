import wizard
import tools
import pooler
import xmlrpclib
import csv
import re
from base_translation.translation import get_language

import config
s = xmlrpclib.Server("http://"config.SERVER+":"+str(config.PORT))

view_form_end = """<?xml version="1.0"?>
    <form string="Information For Contribution">
        <group colspan="2" col="4">
            <field name="draft" colspan="4"/>
            <field name="total" colspan="4"/>
            <field name="propose" colspan="4"/>
        </group>
</form>"""

view_form = """<?xml version="1.0"?>
<form string="Language Selection">
    <image name="gtk-dialog-info" colspan="2"/>
    <group colspan="2" col="4">
    <separator string="Language List" colspan="4"/>
        <label align="0.0" string="Choose a language to upload:" colspan="4"/>
        <field name="lang" colspan="4"/>
        <field name="email_id" colspan="4"/>
        <field name="note" colspan="4"/>        
        <label align="0.0" string="Note that this operation may take a few minutes." colspan="4"/>
    </group>
</form>"""


class wizard_upload_contrib(wizard.interface):
    def _upload_contrib(self, cr, uid, data, context):
        lang = data['form']['lang']
        email_id =data['form']['email_id']
        pattern = '^([a-zA-Z])[a-zA-Z0-9_\.]+@[a-zA-Z0-9]+\.[a-zA-Z]{2,3}$'
        reg = re.compile(pattern)
        reg.search(email_id)
        if not reg.search(email_id):
            raise wizard.except_wizard('Error !', 'Your Email Id is not well-formed')
        ir_translation_contrib = pooler.get_pool(cr.dbname).get('ir.translation.contribution')
        ids = ir_translation_contrib.search(cr,uid,[('lang','=',lang),('state','=','propose'),('upload','=',False)])
        print ids        
        if ids:
            contrib =ir_translation_contrib.read(cr,uid,ids)
            title = ['type','name','res_id','src','value']
            content = map(lambda x:[x['type'],x['name'],x['res_id'],x['src'].decode('utf8').encode('utf8'),x['value'].decode('utf8').encode('utf8')],contrib)
            file_list = s.get_contrib_list()
            n_file = filter(lambda x: not x.find(lang),file_list)
            email_id = email_id.replace('@','_AT_')
            email_id = email_id.replace('.','_DOT_')
            filename = lang+'-'+email_id+'-'+str(len(n_file)+1)+'.csv'
            content.insert(0,title)
            for id in ids:
                ir_translation_contrib.write(cr,uid,id,{'upload':True})
            try :
                s.publish_contrib(content,filename)
            except Exception,e:
                print e
                raise wizard.except_wizard('Error !',"server is not properly configuraed")
        ids = ir_translation_contrib.search(cr,uid,[('lang','=',lang)])
        contrib =ir_translation_contrib.read(cr,uid,ids)
        return {'total':len(ids),'draft':len(filter(lambda x:x['state'] =='draft',contrib)),'propose':len(filter(lambda x:x['state'] =='propose',contrib))}

    def _get_language(sel, cr, uid, context):
        return get_language(cr,uid,context,model='ir_translation_contribution')

    fields_form = {
        'lang': {'string':'Language', 'type':'selection', 'selection':_get_language,'required':True},
        'note': {'string':'Note','type':'text'},
        'email_id':{'string':"Contributor's Email-ID",'type':'char','size':64,'required':True},
    }
    
    fields_form_end = {
        'draft': {'type': 'integer', 'string': 'Number of Draft Translation', 'readonly': True},
        'total': {'type': 'integer', 'string': 'Number of Translation', 'readonly': True},
        'propose': {'type': 'integer', 'string': 'Number of Translation Uploaded(Propose Translation)', 'readonly': True},        
    }    

    states = {
        'init': {
            'actions': [], 
            'result': {'type': 'form', 'arch': view_form, 'fields': fields_form,
                'state': [
                    ('end', 'Cancel', 'gtk-cancel'),
                    ('start', 'Upload Contribution', 'gtk-ok', True)
                ]
            }
        },        
        'start': {
            'actions': [_upload_contrib],
            'result': {'type': 'form', 'arch': view_form_end, 'fields': fields_form_end,
                'state': [
                    ('end', 'Ok', 'gtk-ok', True)
                ]
            }
        },
    }
wizard_upload_contrib('upload.contrib')
