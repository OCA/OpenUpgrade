# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution	
#    Copyright (C) 2004-2008 Tiny SPRL (<http://tiny.be>). All Rights Reserved
#    $Id$
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
import wizard
import tools
import pooler
import xmlrpclib
import csv
import re
import random
import base_translation.translation
import config

s = xmlrpclib.Server("http://"+config.SERVER+":"+str(config.PORT))

view_form_end = """<?xml version="1.0"?>
    <form string="Information For Contribution">
        <group colspan="2" col="4">
            <field name="draft" colspan="4"/>
            <field name="total" colspan="4"/>
            <field name="propose" colspan="4"/>
        </group>
    <label align="0.5" string="For more information about translation process ,you can consult : http://openerp.com/wiki/index.php/Translation_Process" colspan="4"/>
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
        <field name="version" colspan="4"/>
        <field name="profile" colspan="4"/>     
        <label align="0.0" string="Note that this operation may take a few minutes." colspan="4"/>
    </group>
    <label align="0.5" string="For more information about translation process ,you can consult : http://openerp.com/wiki/index.php/Translation_Process" colspan="4"/>
</form>"""


class wizard_upload_contrib(wizard.interface):
    
    def email_check(self,email):
        pattern = '^([a-zA-Z])[a-zA-Z0-9_\.]+@[a-zA-Z0-9]+\.[a-zA-Z]{2,3}$'
        reg = re.compile(pattern)
        return reg.search(email)
        
    def _upload_contrib(self, cr, uid, data, context):
        lang = data['form']['lang']
        email_id =data['form']['email_id']
        version = data['form']['version']
        profile = data['form']['profile']
        if not self.email_check(email_id):
            raise wizard.except_wizard('Error !', 'Your Email Id is not well-formed')
        ir_translation_contrib = pooler.get_pool(cr.dbname).get('ir.translation.contribution')
        sql = "select id from ir_translation_contribution where lang='%s' and state='propose' and upload=False"%lang
        cr.execute(sql)
        ids = map(lambda x:x[0],cr.fetchall())
        if not ids:
            raise wizard.except_wizard('Error !', 'There are no contributions to upload in repository')
        contrib =ir_translation_contrib.read(cr,uid,ids)
        content = map(lambda x:{'type':x['type'],'name':x['name'],'res_id':x['res_id'],'src':x['src'].decode('utf8').encode('utf8'),'value':x['value'].decode('utf8').encode('utf8')},contrib)
        email_id = email_id.replace('@','_AT_')
        email_id = email_id.replace('.','_DOT_')
        filename = lang+'-'+email_id+'-'#+str(random.randint(0,100))+'.csv'
        try :
            s.publish_contrib(lang,version,profile,filename,content)
        except Exception,e:
            print e
            raise wizard.except_wizard('Error !',"server is not properly configuraed")
        if len(ids)>1:
            ids = str(tuple(ids))
        else :
            ids = "("+str(ids[0])+")"
        sql = "UPDATE ir_translation_contribution SET upload=True where id in %s"%ids
        cr.execute(sql)
        ids = ir_translation_contrib.search(cr,uid,[('lang','=',lang)])
        contrib =ir_translation_contrib.read(cr,uid,ids)
        return {'total':len(ids),'draft':len(filter(lambda x:x['state'] =='draft',contrib)),'propose':len(filter(lambda x:x['state'] =='propose',contrib))}

    def _get_language(sel, cr, uid, context):
        return base_translation.translation.get_language(cr,uid,context,model='ir_translation_contribution')
    
    def _get_version(self, cr, uid,context):
        return base_translation.translation.get_version(cr,uid,context)
    
    def _get_profile(self,cr,uid,context):
        return base_translation.translation.get_profile(cr,uid,context)

    fields_form = {
        'lang': {'string':'Language', 'type':'selection', 'selection':_get_language,'required':True},
        'note': {'string':'Note','type':'text'},
        'email_id':{'string':"Contributor's Email-ID",'type':'char','size':64,'required':True},
        'version':{'string':"Version",'type':'selection', 'selection':_get_version,'required':True},
        'profile':{'string':"Profile",'type':'selection', 'selection':_get_profile,'required':True},        
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
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

