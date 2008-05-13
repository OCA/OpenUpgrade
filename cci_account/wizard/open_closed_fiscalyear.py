import wizard
import netsvc
import pooler
from osv import fields, osv

form = """<?xml version="1.0"?>
<form string="Entries">
    <label string="Entries Removed"/>
</form>
"""

def _remove_entries(self, cr, uid, data, context):
    pool = pooler.get_pool(cr.dbname)
    ids_journal = pool.get('account.journal').search(cr, uid, [('centralisation', '=', True)])
    if not ids_journal:
        raise wizard.except_wizard('Warning', 'There is no centralised counterpart journal available ')
    ids_move = pool.get('account.move.line').search(cr,uid,[('journal_id','in',ids_journal)])
    pool.get('account.move.line').unlink(cr,uid,ids_move)
    return {}

class open_closed_fiscal(wizard.interface):
    states = {
        'init' : {
               'actions' : [_remove_entries],
               'result': {'type': 'form', 'arch': form, 'fields': {}, 'state':[('end','Ok')]}
            },
    }
open_closed_fiscal("cci_account.open_closed_fiscal")