import time
import wizard
import netsvc
import pooler
from osv.orm import browse_record

draft2posted_form = """<?xml version="1.0"?>
<form string="Draft To Posted">
    <separator colspan="4" string="change State : Draft to Posted " />
</form>
"""

draft2posted_fields = {

}
def _draft2posted(self, cr, uid, data, context):
        cheque_pool = pooler.get_pool(cr.dbname).get('account.loan.bank.cheque')
        wf_service = netsvc.LocalService("workflow")
        for o in cheque_pool.browse(cr, uid, data['ids'], context):
            if o.state=='draft':
                wf_service.trg_validate(uid, 'account.loan.bank.cheque', o.id, 'post_bank', cr)
        return {}

class change_cheque_state(wizard.interface):
    states = {
        'init' : {
            'actions' : [],
            'result' : {'type' : 'form',
                    'arch' : draft2posted_form,
                    'fields' : {},
                    'state' : [('end', 'Cancel'),('draft2posted', 'Draft To Posted') ]}
        },
        'draft2posted' : {
            'actions' : [],
            'result' : {'type' : 'action',
                    'action' : _draft2posted,
                    'state' : 'end'}
        },
    }
change_cheque_state('account.bank.cheque.process')