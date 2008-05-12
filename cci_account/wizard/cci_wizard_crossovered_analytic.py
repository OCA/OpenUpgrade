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
    'journal': {'string':'Analytic Journal', 'type':'many2one', 'relation':'account.analytic.journal'},
    'ref' :{'string':'Analytic Account Ref.', 'type':'many2one', 'relation':'account.analytic.account','required':True},
   }

class wizard_crossovered_analytic(wizard.interface):

    states = {
        'init': {
            'actions': [],
            'result': {'type':'form', 'arch':form, 'fields':fields, 'state':[('end','Cancel'),('print','Print')]},
        },
        'print': {
            'actions': [],
            'result': {'type':'print', 'report':'account.analytic.account.crossovered.analytic', 'state':'end'},
        },
    }

wizard_crossovered_analytic('wizard.cci.crossovered.analytic')

