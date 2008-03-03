import wizard
import tools
import xmlrpclib
import base64
import csv
import pooler

s = xmlrpclib.Server("http://192.168.0.4:8000")


view_form_end = """<?xml version="1.0"?>
<form string="Language file loaded.">
    <image name="gtk-dialog-info" colspan="2"/>
    <group colspan="2" col="4">
        <separator string="Installation done" colspan="4"/>
        <label align="0.0" string="Csv file for the selected language has been successfully reviewed with the i18n file" colspan="4"/>
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

class wizard_review_proposed_contributions(wizard.interface):
    def _review_difference(self, cr, uid, data, context):
        lang = data['form']['lang']
        ir_translation = pooler.get_pool(cr.dbname).get('ir.translation')
        ids = ir_translation.search(cr,uid,[('lang','=',lang)])
        res = ir_translation.read(cr,uid,ids,['res_id','type','name','value','src'])
        filename = tools.config["root_path"] + "/i18n/" + lang + ".csv"
        reader = csv.DictReader(open(filename,'r'),delimiter=',')
        new_res = []     
        new_res.append(map(lambda x:{'res_id':x['res_id'],'type':x['type'],'name':x['name'],'value':x['value'],'src':x['src']},res))
   
#        for r in reader:
#            print r
        diff = []
        for r in new_res:
            print r
            if r in reader:
                continue
            diff.append(r)
#        print "=========",diff
        return {}
    
#here res_id create problem to compare
#{'res_id': '0', 'type': 'wizard_button', 'name': 'hr.timesheet.invoice.account.analytic.account.cost_ledger.report,init,report', 'value': '', 'src': 'Print'}
#{'type': 'view', 'res_id': 0, 'name': 'hr.employee', 'value': 'Notities', 'src': 'Notes'}    
    
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
                    ('start', 'Review Difference', 'gtk-ok', True)
                ]
            }
        },
        'start': {
            'actions': [_review_difference],
            'result': {'type': 'form', 'arch': view_form_end, 'fields': {},
                'state': [
                    ('end', 'Ok', 'gtk-ok', True)
                ]
            }
        },
     }
wizard_review_proposed_contributions('review.proposed.contributions')