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
import netsvc
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

warning_message = """<?xml version="1.0"?> 
    <form string="!!! Warning"> 
        <image name="gtk-dialog-info" colspan="2"/> 
        <group colspan="2" col="4"> 
            <separator string="%s" colspan="4"/> 
            <label align="0.0" string="%s" colspan="4"/> 
        </group>
    <label align="0.5" string="For more information about translation process ,you can consult : http://openerp.com/wiki/index.php/Translation_Process" colspan="4"/>
    </form>"""

view_form = """<?xml version="1.0"?>
<form string="Language Selection">
    <image name="gtk-dialog-info" colspan="2"/>
    <group colspan="2" col="4">
    <separator string="Language List" colspan="4"/>
        <label align="0.0" string="Choose a language to install:" colspan="4"/>
        <field name="lang" colspan="4"/>
        <field name="password" colspan="4" />
        <field name="version" colspan="4" />
        <field name="profile" colspan="4" />
        <label align="0.0" string="Note that this operation may take a few minutes." colspan="4"/>
    </group>
    <label align="0.5" string="For more information about translation process ,you can consult : http://openerp.com/wiki/index.php/Translation_Process" colspan="4"/>
</form>"""

view_file_form = """<?xml version="1.0"?>
<form string="Contribution Selection">
    <image name="gtk-dialog-info" colspan="2"/>
    <group colspan="2" col="4">
    <separator string="Contribution List" colspan="4"/>
        <label align="0.0" string="Choose a Contribution to install:" colspan="4"/>
        <field name="contrib" colspan="4"/>
        <label align="0.0" string="Note that this operation may take a few minutes." colspan="4"/>
    </group>
    <label align="0.5" string="For more information about translation process ,you can consult : http://openerp.com/wiki/index.php/Translation_Process" colspan="4"/>
</form>"""

class wizard_download_file_for_publish(wizard.interface):
    def _lang_install(self, cr, uid, data, context):
        fname = data['form']['contrib']
        ir_translation_contrib = pooler.get_pool(cr.dbname).get('ir.translation.contribution')        
        try :
            contrib = s.get_contrib(self.user,self.password,self.lang,self.version,self.profile,fname)
            if not contrib :
                raise wizard.except_wizard('Error !!', 'Bad User name or Passsword or you are not authorised for this language')
            
#It is assumed that res_id is properly set and we dnt need to apply any further calculation for it

            for c in contrib :
                vals = {}
                ids = ir_translation_contrib.search(cr,uid,[('type','=',c['type']),('name','=',c['name']),('src','=',c['src']),('lang','=',self.lang)])
                if ids:
                    ir_translation_contrib.write(cr,uid,ids,{'value':c['value'],'src':c['src']})
                if not ids:
                    vals['type']=c['type']
                    vals['name']=c['name']
                    vals['src']=c['src']
                    vals['value']=c['value']
                    vals['res_id']=c['res_id']
                    vals['lang'] = self.lang
                    id = ir_translation_contrib.create(cr,uid,vals)
                    wf_service = netsvc.LocalService("workflow")
                    wf_service.trg_validate(uid, 'ir.translation.contribution', id, 'button_propose', cr)
                    
         #still working to show correct error message when server is not responding properly
         
        except Exception,e:
            if e.__dict__.has_key('name'):
                raise wizard.except_wizard('Error !',e.value)
            else:
                print e
                raise wizard.except_wizard('Error !',"server is not properly configuraed")
        return {}
    
    def lang_checking(self,cr,uid,data,context):
        self.password =data['form']['password']
        self.lang =data['form']['lang']
        self.user = pooler.get_pool(cr.dbname).get('res.users').read(cr,uid,uid,['login'])['login']
        if not s.verify_user(self.user,self.password,self.lang):
            raise wizard.except_wizard('Error !!', 'Bad User name or Passsword or you are not authorised for this language')
        self.version = data['form']['version']
        self.profile = data['form']['profile']        
        cr.execute('select distinct(lang) from ir_translation_contribution')
        lang = cr.fetchall()
        if filter(lambda x : self.lang==x[0],lang):
            return 'same_lang_loaded'
        else:
            return 'version_check'
        
    def _checking(self,cr,uid,data,context):
        file_list = s.get_contrib_revision(self.user,self.password,self.lang,self.version,self.profile)
        if file_list:
            lang_dict = tools.get_languages()
            self.file_list = [(lang[0], lang_dict.get(lang[1], lang[1])+' by '+lang[2]+' at R '+lang[3]) for lang in file_list]    
            return 'file_selection'
        return 'version_not_found'

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
    
    def _get_contrib(self,cr, uid,context):
        return self.file_list    
    
    fields_file_form = {
        'contrib': {'string':'Contribution', 'type':'selection', 'selection':_get_contrib,'required':True},
    }
    states = {
        'init': {
            'actions': [], 
            'result': {'type': 'form', 'arch': view_form, 'fields': fields_form,
                'state': [
                    ('end', 'Cancel', 'gtk-cancel'),
                    ('language_check', 'Select Version', 'gtk-ok', True)
                    ]
                    }
                },
            'language_check': {
                'actions': [],
                'result' : {'type': 'choice', 'next_state': lang_checking }
                } , 
                
            'version_check': {
                'actions': [],
                'result' : {'type': 'choice', 'next_state': _checking }
                } , 

            'same_lang_loaded' : {
                'actions':[],
                'result' :{'type':'form',
                        'arch':warning_message % 
                                  ('One Version is loaded',
                                   "One version of this language is already loaded ,If you will load other than that it may create problem."),
                        'fields':{},
                        'state':[
                                 ('end','Cancel','gtk-cancel'),
                                 ('version_check','Continue....', 'gtk-ok', True)
                                 ]
                        }
                },
            'version_not_found' : {
                'actions':[],
                'result' :{'type':'form',
                       'arch':warning_message % 
                           ('Revision Not Found',
                            "Revision for the selected language is not found either in version or in profile ")
                      ,'fields':{},
                      'state':[
                             ('end','Cancel','gtk-cancel'),
                             ('init','Select Again', 'gtk-ok', True)
                             ]
                    }
            },            
        'file_selection': {
            'actions': [], 
            'result': {'type': 'form', 'arch': view_file_form, 'fields': fields_file_form,
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
wizard_download_file_for_publish('download.publish.file')
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

