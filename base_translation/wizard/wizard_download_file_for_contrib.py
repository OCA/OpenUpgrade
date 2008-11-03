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
import csv
import base64
import xmlrpclib
import pooler
import config
import base_translation.translation

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

warning_message ="""<?xml version="1.0"?> 
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
        <label align="0.0" string="Choose a Version and Profile for language :" colspan="4"/>
        <field name="lang" colspan="4"/>
        <field name="version" colspan="4" /> 
        <field name="profile" colspan="4"/>
    </group>
    <label align="0.5" string="For more information about translation process ,you can consult : http://openerp.com/wiki/index.php/Translation_Process" colspan="4"/>
</form>"""

view_form_version = """<?xml version="1.0"?>
<form string="Language Selection">
    <image name="gtk-dialog-info" colspan="2"/>
    <group colspan="2" col="4">
    <separator string="Language List" colspan="4"/>
        <label align="0.0" string="Choose a Version:" colspan="4"/>
        <field name="revision" colspan="4" />
        <label align="0.0" string="Note that this operation may take a few minutes." colspan="4"/>
    </group>
    <label align="0.5" string="For more information about translation process ,you can consult : http://openerp.com/wiki/index.php/Translation_Process" colspan="4"/>
    
</form>"""

class wizard_download_file_for_contrib(wizard.interface):
    def _lang_install(self, cr, uid, data, context):
        revision = data['form']['revision']
        try :
            text = s.get_release(self.lang,self.version,self.profile,revision)
            filename = tools.config["root_path"] + "/i18n/" + self.lang + ".csv"
            
            h_row = {'type': 'type', 'res_id': 'res_id', 'name': 'name', 'value': 'value', 'src': 'src'}
            f = open(filename,'wb')
            fieldnames=tuple(text[0].keys())
            outwriter = csv.DictWriter(f, fieldnames=fieldnames)
            outwriter.writerow(h_row)
            for t in text:
                t['value'] = t['value'].encode('utf8')
                t['src']=t['src'].encode('utf8')
            outwriter.writerows(text)
            
            tools.trans_load(cr.dbname, filename, self.lang)
                            
        except Exception,e:
            print e
            raise wizard.except_wizard('Error !',"server is not properly configuraed")
        return {}

    def _get_language(self, cr,uid,context):
        return base_translation.translation.get_language(cr,uid,context,user='contributor')
    
    def _get_version(self, cr, uid,context):
        return base_translation.translation.get_version(cr,uid,context)
    
    def _get_profile(self,cr,uid,context):
        return base_translation.translation.get_profile(cr,uid,context)
    
    def lang_checking(self,cr,uid,data,context):
        self.lang = data['form']['lang']
        self.version = data['form']['version']
        self.profile = data['form']['profile']
        cr.execute('select distinct(lang) from ir_translation_contribution')
        lang = cr.fetchall()
        if filter(lambda x : self.lang==x[0],lang):
            return 'same_lang_loaded'
        else:
            return 'version_check'
        
    def _checking(self,cr,uid,data,context):
        self.revision = s.get_publish_revision(self.lang,self.version,self.profile)
        if self.revision:
             return 'version'
        return 'version_not_found' 
    
    fields_form = {
        'lang': {'string':'Language', 'type':'selection', 'selection':_get_language,'required':True},  #',on_change':'_get_version','required':True},
        'version': {'string':'Version', 'type':'selection', 'selection':_get_version,'required':True}, #,'on_change':'_get_profile','required':True},        
        'profile': {'string':'Profile', 'type':'selection', 'selection':_get_profile,'required':True},         
    }
    
    def _get_revision(self,cr,uid,context):
        return self.revision
            
    fields_form_version = {
        'revision': {'string':'Revision', 'type':'selection', 'selection':_get_revision,'required':True},
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
                       'arch': warning_message % 
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
                       'arch': warning_message % 
                           ('Revision Not Found',
                            "Revision for the selected language is not found either in version or in profile ")
                        ,'fields':{},
                    'state':[
                             ('end','Cancel','gtk-cancel'),
                             ('init','Select Again', 'gtk-ok', True)
                             ]
                    }
            },            
        'version': {
            'actions': [], 
            'result': {'type': 'form', 'arch': view_form_version, 'fields': fields_form_version,
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
wizard_download_file_for_contrib('download.contrib.file')
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

