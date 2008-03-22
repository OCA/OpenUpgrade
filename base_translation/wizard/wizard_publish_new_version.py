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
        <field name="password" colspan="4"/>
        <label align="0.0" string="Note that this operation may take a few minutes." colspan="4"/>
    </group>
</form>"""


class wizard_publish_new_version(wizard.interface):
    def _publish_new_version(self, cr, uid, data, context):
        lang = data['form']['lang']
        pwd = data['form']['password']
        user = pooler.get_pool(cr.dbname).get('res.users').read(cr,uid,uid,['login'])['login']
        ir_translation_contrib = pooler.get_pool(cr.dbname).get('ir.translation.contribution')
        ids = ir_translation_contrib.search(cr,uid,[('lang','=',lang),('state','=','accept')])        
        if ids:
            publish = ir_translation_contrib.read(cr,uid,ids,title)
            try :
                s.publish_release(user,pwd,publish,lang+'.csv')
            except Exception,e:
                print e
                raise wizard.except_wizard('Error !',"server is not properly configuraed")
        return {'total':0,'draft':0,'propose':0}

    def _get_language(sel, cr, uid, context):
        return get_language(cr,uid,context,user='maintainer_publish')

    fields_form = {
        'lang': {'string':'Language', 'type':'selection', 'selection':_get_language,'required':True},
        'password':{'strin':'Password','type':'char','size':20}
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
                    ('start', 'Publish File', 'gtk-ok', True)
                ]
            }
        },        
        'start': {
            'actions': [_publish_new_version],
            'result': {'type': 'form', 'arch': view_form_end, 'fields': fields_form_end,
                'state': [
                    ('end', 'Ok', 'gtk-ok', True)
                ]
            }
        },
    }
wizard_publish_new_version('publish.new.version')
