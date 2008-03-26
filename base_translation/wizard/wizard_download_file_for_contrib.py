import wizard
import tools
import csv
import base64
import xmlrpclib
import config

from base_translation.translation import get_language

s = xmlrpclib.Server("http://"+config.SERVER+":"+str(config.PORT))

import wizard
import tools
import csv
import base64
import xmlrpclib
import pooler
import base_translation.translation

s = xmlrpclib.Server("http://192.168.0.4:8000")

view_form_end = """<?xml version="1.0"?>
<form string="Language file loaded.">
    <image name="gtk-dialog-info" colspan="2"/>
    <group colspan="2" col="4">
        <separator string="Installation done" colspan="4"/>
        <label align="0.0" string="Csv file for the selected language has been successfully installed in i18n" colspan="4"/>
    </group>
</form>"""

view_form = """<?xml version="1.0"?>
<form string="Language Selection">
    <image name="gtk-dialog-info" colspan="2"/>
    <group colspan="2" col="4">
    <separator string="Language List" colspan="4"/>
        <label align="0.0" string="Choose a Version and Profile for language :" colspan="4"/>
        <field name="lang" colspan="4" />
        <field name="version" colspan="4"/>
        <field name="profile" colspan="4"/>
        <label align="0.0" string="Note that this operation may take a few minutes." colspan="4"/>
    </group>
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
</form>"""

class wizard_download_file_for_contrib(wizard.interface):
    def _lang_install(self, cr, uid, data, context):
        revision = data['form']['revision']
        try :
            text = s.get_release(self.lang,self.version,self.profile,revision)
            filename = tools.config["root_path"] + "/i18n/" + self.lang + ".csv"
            fp = file(filename,'wb').write(text.encode('utf8'))
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
    
    def _set_param(self,cr,uid,data,context):
        self.lang = data['form']['lang']
        self.version = data['form']['version']
        self.profile = data['form']['profile']
        return {}

    fields_form = {
        'lang': {'string':'Language', 'type':'selection', 'selection':_get_language,'required':True},
        'version': {'string':'Version', 'type':'selection', 'selection':_get_version,'required':True},        
        'profile': {'string':'Profile', 'type':'selection', 'selection':_get_profile,'required':True},         
    }
    
    def _get_revision(self,cr,uid,context):
        revision = s.get_publish_revision(self.lang,self.version,self.profile)
        if not revision:
            raise wizard.except_wizard('Info !', 'No revision Found')
        return revision
    
    fields_form_version = {
        'revision': {'string':'Revision', 'type':'selection', 'selection':_get_revision,'required':True},
    }

    states = {
        'init': {
            'actions': [], 
            'result': {'type': 'form', 'arch': view_form, 'fields': fields_form,
                'state': [
                          ('end', 'Cancel', 'gtk-cancel'),
                          ('version', 'Select Version', 'gtk-ok', True)
                        ]
                    }
                },
        'version': {
            'actions': [_set_param], 
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
