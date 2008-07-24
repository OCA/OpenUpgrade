# -*- encoding: utf-8 -*-
import wizard
import pooler

def _offer_documents(self, cr, uid, data, context):
    offer_id = data['id']
    pool = pooler.get_pool(cr.dbname)
    step_id = pool.get('dm.offer.step').search(cr,uid,[('offer_id','=',offer_id)])
    offer_document = pool.get('ir.attachment').search(cr,uid,[('res_id','=',offer_id),('res_model','=','dm.offer')])
    document_ids =pool.get('ir.attachment').search(cr,uid,[('res_id','in',step_id),('res_model','=','dm.offer.step')])
    document_ids.extend(offer_document)
    value = {
        'domain': [('id', 'in',document_ids)],
        'name': 'Documents',
        'view_type': 'form',
        'view_mode': 'tree,form',
        'res_model': 'ir.attachment',
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
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

