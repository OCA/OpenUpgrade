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

def _offer_documents(self, cr, uid, data, context):
    offer_id = data['id']
    pool = pooler.get_pool(cr.dbname)
    step_id = pool.get('dm.offer.step').search(cr,uid,[('offer_id','=',offer_id)])
#    document_ids =pool.get('dm.offer.document').search(cr,uid,[('step_id','in',step_id)])
    value = {
        'domain': [('step_id','in',step_id)],
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
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

