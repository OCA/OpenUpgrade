import wizard
import pooler


dates_form = '''<?xml version="1.0"?>
<form string="Indian Account Balance Sheet">
    <field name="fiscalyear" colspan="4"/>
    <field name="empty_account" colspan="2"/>
    <field name="periods" colspan="4"/>
</form>'''

dates_fields = {
    'fiscalyear': {'string': 'Fiscal year', 'type': 'many2one', 'relation': 'account.fiscalyear',
        'help': 'Keep empty for all open fiscal year'},
    'empty_account':{'string':'Include Empty Account:', 'type':'boolean'},
    'periods': {'string': 'Periods', 'type': 'many2many', 'relation': 'account.period', 'help': 'All periods if empty'}
}

class wizard_in_pl_report_tiny(wizard.interface):
    def _get_defaults(self, cr, uid, data, context):
        fiscalyear_obj = pooler.get_pool(cr.dbname).get('account.fiscalyear')
        data['form']['fiscalyear'] = fiscalyear_obj.find(cr, uid)
        return data['form']

    states = {
        'init': {
            'actions': [_get_defaults],
            'result': {'type':'form', 'arch':dates_form, 'fields':dates_fields, 'state':[('end','Cancel'),('report','Print')]}
        },
        'report': {
            'actions': [],
            'result': {'type':'print', 'report':'report.balance.sheet.tiny', 'state':'end'}
        }
    }
wizard_in_pl_report_tiny('report.balance.sheet2')
