# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution	
#    Copyright (C) 2004-2008 Tiny SPRL (<http://tiny.be>). All Rights Reserved
#    $Id$
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
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
