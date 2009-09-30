import time
import wizard


loan_form = '''<?xml version="1.0"?>
<form string="Select partner">
    <field name="partner_id"/>
</form>'''

loan_fields = {
    'partner_id': {'string':'Partner', 'type':'many2one', 'relation': 'res.partner', 'required':True},
}

class wizard_report(wizard.interface):
    states = {
        'init': {
            'actions': [],
            'result': {'type':'form', 'arch':loan_form, 'fields':loan_fields, 'state':[('end','Cancel'),('report','Print Loan Report.')]}
        },
        'report': {
            'actions': [],
            'result': {'type':'print', 'report':'account.partner.loan', 'state':'end'}
        }
    }
wizard_report('account.partner.loan')