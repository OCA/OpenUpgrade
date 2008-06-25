import wizard
import pooler

def _offer_documents(self, cr, uid, data, context):
    offer_id = data['id']
    pool = pooler.get_pool(cr.dbname)
    step_id = pool.get('dm.offer.step').search(cr,uid,[('offer_id','=',offer_id)])
    step = pool.get('dm.offer.step').browse(cr,uid,step_id)
    document_ids =[]
    for s in step:
        document_ids.extend(map(lambda d:d.id,s.document_ids))
    value = {
        'domain': [('id', 'in',document_ids)],
        'name': 'Documents',
        'view_type': 'form',
        'view_mode': 'tree,form',
        'res_model': 'dm.offer.document',
        'context': { },
        'type': 'ir.actions.act_window'
    }
    return value

class wizard_offer_documents(wizard.interface):
    states = {
        'init': {
            'actions': [],
            'result': {
                'type': 'action',
                'action': _offer_documents,
                'state': 'end'
            }
        },
    }
wizard_offer_documents("wizard_offer_documents")
