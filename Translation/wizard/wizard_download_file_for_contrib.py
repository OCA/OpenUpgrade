import wizard
import tools
import xmlrpclib
import base64
import csv

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
        <label align="0.0" string="Note that this operation may take a few minutes." colspan="4"/>
    </group>
</form>"""


class wizard_download_file_for_contrib(wizard.interface):
    def _lang_install(self, cr, uid, data, context):
        lang = data['form']['lang']
        if lang and lang != 'en_EN':
            fname = lang + ".csv"
            text = base64.decodestring(s.get_release(fname))
            filename = tools.config["root_path"] + "/i18n/" + lang + ".csv"
            fp = file(filename,'wb').write(text)
            tools.trans_load(cr.dbname, filename, lang)
        return {}

    def _get_language(sel, cr, uid, context):
        f_list = []
        file_list = s.get_publish_list()
        for f in file_list : f_list.append(f.replace('.csv',''))
        lang_dict = tools.get_languages()
        return [(lang, lang_dict.get(lang, lang)) for lang in f_list]

    fields_form = {
        'lang': {'string':'Language', 'type':'selection', 'selection':_get_language,
        },
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
wizard_download_file_for_contrib('download.contib.file')
