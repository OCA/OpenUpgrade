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
</form>"""

view_file_form = """<?xml version="1.0"?>
<form string="Contribution Selection">
    <image name="gtk-dialog-info" colspan="2"/>
    <group colspan="2" col="4">
    <separator string="Contribution List" colspan="4"/>
        <label align="0.0" string="Choose a Contribution to install:" colspan="4"/>
        <field name="file" colspan="4"/>
        <label align="0.0" string="Note that this operation may take a few minutes." colspan="4"/>
    </group>
</form>"""

class wizard_publish_new_version(wizard.interface):
    def _lang_install(self, cr, uid, data, context):
        file_re= data['form']['file']
        print self.lang,self.user,self.password
        ir_translation = pooler.get_pool(cr.dbname).get('ir.translation')
        ir_translation_contrib = pooler.get_pool(cr.dbname).get('ir.translation.contribution')        
        try :
            fname = self.lang+'-'+file_re+'.csv'
            content = s.get_contrib(self.user,self.password,self.lang,self.version,self.profile,fname,True)
            if not content :
                raise wizard.except_wizard('Error !!', 'Bad User name or Passsword or you are not authorised for this language')
            new_content = map(lambda x:x,content)
            ids = ir_translation_contrib.search(cr,uid,[('lang','=',self.lang),('state','=','accept')])
            if ids:
                contrib = ir_translation_contrib.read(cr,uid,ids)
                new_contrib =map(lambda x:{'type':x['type'],'name':x['name'],'res_id':x['res_id'],'src':x['src'],'value':x['value']},contrib)
                
#It is assumed that except value nothing is changed

            for c in new_contrib :
                for n in new_content:
                    if c['type']==n['type'] and c['src']==n['src'] and c['name']==n['name']:
                        n['value']=c['value']
            result = s.publish_release(self.user,self.password,self.lang,self.version,self.profile,fname,new_content)
            if not result: 
                raise wizard.except_wizard('Error !!', 'Bad User name or Passsword or you are not authorised for this language')
            ir_translation_contrib.write(cr,uid,ids,{'state':'done'})
            
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
    
    def _get_file(self,cr, uid,context):
        if not s.verify_user(self.user,self.password,self.lang):
            raise wizard.except_wizard('Error !!', 'Bad User name or Passsword or you are not authorised for this language')
        file_list = s.get_publish_revision(self.lang,self.version,self.profile)
        if not file_list:
            raise wizard.except_wizard('Info !!', 'No File Found')
        return file_list    
    
    fields_file_form = {
        'file': {'string':'Contribution', 'type':'selection', 'selection':_get_file,'required':True},
    }
    states = {
        'init': {
            'actions': [], 
            'result': {'type': 'form', 'arch': view_form, 'fields': fields_form,
                'state': [
                    ('end', 'Cancel', 'gtk-cancel'),
                    ('file_selection', 'Select Version', 'gtk-ok', True)
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
wizard_publish_new_version('publish.new.version')