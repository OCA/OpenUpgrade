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
import xmlrpclib
import base64
import pooler
import tools
import base_translation.translation 

import config
s = xmlrpclib.Server("http://"+config.SERVER+":"+str(config.PORT))

view_form_end = """<?xml version="1.0"?>
<form string="Language file loaded.">
    <image name="gtk-dialog-info" colspan="2"/>
    <group colspan="2" col="4">
        <separator string="Installation done" colspan="4"/>
        <label align="0.0" string="Csv file for the selected language has been successfully installed in i18n" colspan="4"/>
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
        <field name="password" colspan="4" />
        <field name="version" colspan="4" />
        <field name="profile" colspan="4" />
        <label align="0.0" string="Note that this operation may take a few minutes." colspan="4"/>
    </group>
    <label align="0.5" string="For more information about translation process ,you can consult : http://openerp.com/wiki/index.php/Translation_Process" colspan="4"/>
</form>"""

class wizard_publish_new_version(wizard.interface):
    def _lang_install(self, cr, uid, data, context):
        password =data['form']['password']
        lang =data['form']['lang']
        user = pooler.get_pool(cr.dbname).get('res.users').read(cr,uid,uid,['login'])['login']
        if not s.verify_user(user,password,lang):
            raise wizard.except_wizard('Error !!', 'Bad User name or Passsword or you are not authorised for this language')
        version = data['form']['version']
        profile = data['form']['profile']         
        ir_translation_contrib = pooler.get_pool(cr.dbname).get('ir.translation.contribution')        
        ids = ir_translation_contrib.search(cr,uid,[('lang','=',lang),('state','=','accept')])
        if not ids:
            raise wizard.except_wizard('Error !!', 'No contributions are find to upload in main revision')
        contrib = ir_translation_contrib.read(cr,uid,ids,['type','name','res_id','src','value'])
        new_contrib =map(lambda x:{'type':x['type'],'name':x['name'],'res_id':x['res_id'],'src':x['src'],'value':x['value']},contrib)
                
        try :
            result = s.publish_release(user,password,lang,version,profile,new_contrib)
     #still working to show correct error message when server is not responding properly
            
        except Exception,e:
            if e.__dict__.has_key('name'):
                raise wizard.except_wizard('Error !',e.value)
            else:
                print e
                raise wizard.except_wizard('Error !',"server is not properly configuraed")
            ir_translation_contrib.write(cr,uid,ids,{'state':'done'})
        return {}
    

    def _get_language(sel, cr, uid, context):
        return base_translation.translation.get_language(cr,uid,context,user='maintainer')
    
    def _get_version(self, cr, uid,context):
        return base_translation.translation.get_version(cr,uid,context)
    
    def _get_profile(self,cr,uid,context):
        return base_translation.translation.get_profile(cr,uid,context)
    
    fields_form = {
        'lang': {'string':'Language', 'type':'selection', 'selection':_get_language,'required':True},
        'password': {'string':'Password', 'type':'char', 'size':32, 'required':True,'invisible':True},
        'version': {'string':'Version', 'type':'selection', 'selection':_get_version,'required':True},        
        'profile': {'string':'Profile', 'type':'selection', 'selection':_get_profile,'required':True},  
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
            'actions': [_lang_install],
            'result': {'type': 'form', 'arch': view_form_end, 'fields': {},
                'state': [
                    ('end', 'Ok', 'gtk-ok', True)
                ]
            }
        },
    }
wizard_publish_new_version('publish.new.version')
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

