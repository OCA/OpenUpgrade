import wizard
import time
import datetime
import pooler

form = """<?xml version="1.0"?>
<form string="Select Information">
     <field name="date1"/>
     <field name="date2"/>
     <field name="journal"/>
     <field name="ref"/>
</form>"""

fields = {
    'date1': {'string':'Start Date', 'type':'date', 'required':True, 'default': lambda *a: time.strftime('%Y-01-01')},
    'date2': {'string':'End Date', 'type':'date', 'required':True, 'default': lambda *a: time.strftime('%Y-%m-%d')},
    'journal': {'string':'Analytic Journal', 'type':'many2one', 'relation':'account.analytic.journal','domain':[('type','in',['sale','purchase'])]},
    'ref' :{'string':'Analytic Account Ref.', 'type':'many2one', 'relation':'account.analytic.account','required':True},
   }

class wizard_crossovered_analytic(wizard.interface):
    def _checklines(self, cr, uid, data, context):
        cr.execute('select account_id from account_analytic_line')
        res=cr.fetchall()
        acc_ids=[x[0] for x in res]

        obj_acc = pooler.get_pool(cr.dbname).get('account.analytic.account').browse(cr,uid,data['form']['ref'])
        name=obj_acc.name

        if not data['form']['ref'] in acc_ids:
            raise wizard.except_wizard('User Error',"There are no Analytic lines related to  Account '" + name +"'" )
        return {}

    states = {
        'init': {
            'actions': [],
            'result': {'type':'form', 'arch':form, 'fields':fields, 'state':[('end','Cancel'),('print','Print')]},
        },
        'print': {
            'actions': [_checklines],
            'result': {'type':'print', 'report':'account.analytic.account.crossovered.analytic', 'state':'end'},
        },
    }

wizard_crossovered_analytic('wizard.cci.crossovered.analytic')

