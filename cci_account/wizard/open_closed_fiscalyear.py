import wizard
import netsvc
import pooler
from osv import fields, osv

form = """<?xml version="1.0"?>
<form string="Entries">
    <field name="fyear_id"/>
</form>
"""
fields={
    'fyear_id': {'string': 'Fiscal year to open', 'type': 'many2one', 'relation': 'account.fiscalyear', 'required': True},
        }
def _remove_entries(self, cr, uid, data, context):
    pool = pooler.get_pool(cr.dbname)
    data_fyear = pool.get('account.fiscalyear').browse(cr,uid,data['form']['fyear_id'])
    if not data_fyear.period_id:
        raise wizard.except_wizard('Error', 'You should have New Entries journal define in fiscal year')
    period_journal = data_fyear.period_id
    if not period_journal.journal_id.centralisation:
            raise wizard.except_wizard('UserError',
                    'The journal must have centralised counterpart')
    ids_move = pool.get('account.move').search(cr,uid,[('journal_id','=',period_journal.journal_id.id),('period_id','=',period_journal.period_id.id)])
    pool.get('account.move').unlink(cr,uid,ids_move)
    return {}

class open_closed_fiscal(wizard.interface):
    states = {
        'init' : {
               'actions' : [],
               'result': {'type': 'form', 'arch': form, 'fields': fields, 'state':[('end','Cancel'),('open','Open')]}
            },
        'open': {
            'actions': [],
            'result': {'type':'action', 'action':_remove_entries, 'state':'end'},
        },
    }
open_closed_fiscal("cci_account.open_closed_fiscal")