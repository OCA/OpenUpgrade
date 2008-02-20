import time
import wizard

dates_form = '''<?xml version="1.0"?>
<form string="Select Options">
    <field name="date_from"/>
    <field name="date_to"/>
    <field name="report_type" colspan="3"/>
</form>'''

dates_fields = {
    'date_from': {'string':'Start of period', 'type':'date', 'required':True, 'default': lambda *a: time.strftime('%Y-01-01')},
    'date_to': {'string':'End of period', 'type':'date', 'required':True, 'default': lambda *a: time.strftime('%Y-%m-%d')},
    'report_type':{'string':'Select Report Type','type':'selection','selection':[('analytic-full','Analytic Account-Wise Full Information'),('analytic-one','Analytic Account-Wise One line Description')]},
}

class wizard_report(wizard.interface):

    def _default(self, cr, uid, data, context):
        data['form']['report_type']='analytic-full'
        return data['form']

    states = {
        'init': {
            'actions': [_default],
            'result': {'type':'form', 'arch':dates_form, 'fields':dates_fields, 'state':[('end','Cancel'),('report','Print')]}
        },
        'report': {
            'actions': [],
            'result': {'type':'print', 'report':'crossovered.budget.report', 'state':'end'}
        }
    }
wizard_report('wizard.crossovered.budget')