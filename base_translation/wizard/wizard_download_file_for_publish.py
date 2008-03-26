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
</form>"""

class wizard_download_file_for_publish(wizard.interface):
    def _lang_install(self, cr, uid, data, context):
        fname = data['form']['contrib']
        ir_translation = pooler.get_pool(cr.dbname).get('ir.translation')
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
    
    def _set_param(self, cr, uid, data, context):
        self.password =data['form']['password']
        self.lang =data['form']['lang']
        self.user = pooler.get_pool(cr.dbname).get('res.users').read(cr,uid,uid,['login'])['login']
        if not s.verify_user(self.user,self.password,self.lang):
            raise wizard.except_wizard('Error !!', 'Bad User name or Passsword or you are not authorised for this language')
        self.version = data['form']['version']
        self.profile = data['form']['profile']        
        return {}
 
#        return [('test','test')]    

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
        file_list = s.get_contrib_revision(self.user,self.password,self.lang,self.version,self.profile)
        if not file_list:
            raise wizard.except_wizard('Info !!', 'No Contribution Found')
        lang_dict = tools.get_languages()
        return [(lang[0], lang_dict.get(lang[1], lang[1])+' by '+lang[2]+' at R '+lang[3]) for lang in file_list]    
    
    fields_file_form = {
        'contrib': {'string':'Contribution', 'type':'selection', 'selection':_get_contrib,'required':True},
    }
    states = {
        'init': {
            'actions': [], 
            'result': {'type': 'form', 'arch': view_form, 'fields': fields_form,
                'state': [
                    ('end', 'Cancel', 'gtk-cancel'),
                    ('file_selection', 'Select Contribution Version', 'gtk-ok', True)
                ]
            }
        },
        'file_selection': {
            'actions': [_set_param], 
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
