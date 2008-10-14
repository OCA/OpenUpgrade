# -*- encoding: utf-8 -*-
import wizard
import time
import pooler


form = """<?xml version="1.0"?>
<form string="Select No. of Pages For Documents">
    <field name="pages_doc1"/>
    <field name="pages_doc2"/>
</form>"""

fields = {
    'pages_doc1': {'string': 'No. of pages in document1', 'type':'integer', 'required': True},
    'pages_doc2': {'string': 'No. of pages in document2', 'type':'integer', 'required': True},
   }

class wizard_report(wizard.interface):
    def _checkint(self, cr, uid, data, context):

        if data['form']['pages_doc1'] <0 or data['form']['pages_doc2']<0:
            raise wizard.except_wizard('Warning !', 'Please Enter Positive Values!')
        return {}

    states = {
        'init': {
            'actions': [],
            'result': {'type':'form', 'arch':form, 'fields':fields, 'state':[('end','Cancel'),('print','Print')]},
        },
        'print': {
            'actions': [_checkint],
            'result': {'type':'print', 'report':'cci_missions_print_carnet', 'state':'print1'},
        },
        'print1': {
            'actions': [],
            'result': {'type':'print', 'report':'cci_missions_print_carnet1', 'state':'end'},
        },
    }

wizard_report('cci_missions_print_carnet')
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

