import wizard
import tools
import xmlrpclib
import base64
import pooler
from translation.translation import get_language

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
        <label align="0.0" string="Choose a language to install:" colspan="4"/>
        <field name="lang" colspan="4"/>
        <field name="password" colspan="4" />
        <label align="0.0" string="Note that this operation may take a few minutes." colspan="4"/>
    </group>
</form>"""


class wizard_download_file_for_publish(wizard.interface):
    def _lang_install(self, cr, uid, data, context):
        lang = data['form']['lang']
        pwd = data['form']['password']
        user = pooler.get_pool(cr.dbname).get('res.users').read(cr,uid,uid,['login'])['login']
        fname = lang + ".csv"
        try :
            text = s.get_contrib(fname,user,pwd,lang)
            if not text :
                raise wizard.except_wizard('Error !!', 'Bad User name or Passsword or you are not authorised for this language')
            filename = tools.config["root_path"] + "/i18n/" + lang + ".csv"
            tools.trans_load(cr.dbname, filename, lang)                
            fp = file(filename,'wb').write(text.encode('utf8'))
            tools.trans_load(cr.dbname, filename, lang)                
        except Exception,e:
            if e.__dict__.has_key('name'):
                raise wizard.except_wizard('Error !',e.value)
            else:
                raise wizard.except_wizard('Error !',"server is not properly configuraed")
        return {}

    def _get_language(sel, cr, uid, context):
        return get_language(cr,uid,context,user='maintainer')

    fields_form = {
        'lang': {'string':'Language', 'type':'selection', 'selection':_get_language,},
        'password': {'string':'Password', 'type':'char', 'size':32, 'required':True,
        'invisible':True},
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
wizard_download_file_for_publish('download.publish.file')