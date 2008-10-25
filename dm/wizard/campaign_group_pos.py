# -*- encoding: utf-8 -*-
import wizard
import pooler

def _campaign_group_pos(self, cr, uid, data, context):
    campaign_group_id = data['id']
    cr.execute('''SELECT id FROM dm_campaign_purchase_line WHERE campaign_group_id = %d '''% (campaign_group_id, ))
    res = cr.fetchall()
    pline_ids = []
    for r in res:
        pline_ids.append(r[0])
    res2 = []
    for pline_id in pline_ids:
        cr.execute('''SELECT id FROM purchase_order WHERE dm_campaign_purchase_line = %d '''% (pline_id, ))
        result = cr.fetchall()
        for r in result:
            res2.append(r)
    value = {
        'domain': [('id', 'in', res2)],
        'name': 'Purchase Orders',
        'view_type': 'form',
        'view_mode': 'tree,form,calendar',
        'res_model': 'purchase.order',
        'context': { },
        'type': 'ir.actions.act_window'
    }
    return value

class wizard_campaign_group_pos(wizard.interface):
    states = {
        'init': {
            'actions': [],
            'result': {
                'type': 'action',
                'action': _campaign_group_pos,
                'state': 'end'
            }
        },
    }
wizard_campaign_group_pos("wizard_campaign_group_pos")
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
