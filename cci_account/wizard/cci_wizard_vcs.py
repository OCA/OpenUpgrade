# -*- encoding: utf-8 -*-

import wizard
import pooler

_form="""<?xml version="1.0"?>
<form string="Are you sure?" colspan="4">
    <label string="Make Sure that the invoice has invoice number." />
</form>
"""

_fields = {
           }

class wizard_report(wizard.interface):

    def _get_defaults(self, cr, uid, data, context):
        inv_obj = pooler.get_pool(cr.dbname).get('account.invoice')
        for obj_inv in inv_obj.browse(cr,uid,data['ids']):
            if obj_inv.type not in ('out_invoice','out_refund'):
                raise wizard.except_wizard('User Error!','VCS is associated with Customer Invoices and Refund only.')
            if not obj_inv.number:
                raise wizard.except_wizard('Data Insufficient!','No Invoice Number Associated with the Invoice ID '+ str(obj_inv.id) +'!')
        return data['form']

    states = {
        'init': {
            'actions': [_get_defaults],
            'result': {'type':'form', 'arch':_form, 'fields':_fields, 'state':[('report','Ok')]}
        },
        'report': {
            'actions': [],
            'result': {'type':'print', 'report':'cci.vcs', 'state':'end'}
        }
    }
wizard_report('wizard.cci.vcs')
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

