import wizard
import tools
import pooler
import xmlrpclib
import csv
from translation.translation import get_language

s = xmlrpclib.Server("http://192.168.0.4:8000")

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
#    This is not woring 
    def _upload_contrib(self, cr, uid, data, context):
        lang = data['form']['lang']
        email_id =data['form']['email_id']
        ir_translation_contrib = pooler.get_pool(cr.dbname).get('ir.translation.contribution')
        ids = ir_translation_contrib.search(cr,uid,[('lang','=',lang)])
        contrib =ir_translation_contrib.read(cr,uid,ids)
        title = ['type','name','res_id','src','value']
        content = map(lambda x:[x['type'],x['name'],x['res_id'],x['src'],x['value']],contrib)
        filename = lang+'.csv'
        s.publish_contrib(content.insert(0,title),filename)
        
        read_text = csv.reader(open('/home/tiny/contrib/fr_FR.csv','r'),delimiter=',')
        for r in read_text:
            print r
        return {'total':len(ids),'draft':len(filter(lambda x:x['state'] =='draft',contrib)),'propose':len(filter(lambda x:x['state'] =='propose',contrib))}

    def _get_language(sel, cr, uid, context):
        return get_language(cr,uid,context)

    fields_form = {
        'lang': {'string':'Language', 'type':'selection', 'selection':_get_language,'required':True},
        'note': {'string':'Note','type':'text'},
        'email_id':{'string':"Contributor's Email-ID",'type':'char','size':64,'required':True},
    }
    
    fields_form_end = {
        'draft': {'type': 'integer', 'string': 'Number of Draft Translation', 'readonly': True},
        'total': {'type': 'integer', 'string': 'Number of Translation', 'readonly': True},
        'propose': {'type': 'integer', 'string': 'Number of Propose Translation', 'readonly': True},        
    }    

    states = {
        'init': {
            'actions': [], 
            'result': {'type': 'form', 'arch': view_form, 'fields': fields_form,
                'state': [
                    ('end', 'Cancel', 'gtk-cancel'),
                    ('start', 'Download File', 'gtk-ok', True)
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