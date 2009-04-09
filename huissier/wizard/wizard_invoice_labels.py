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
import netsvc
import pooler

# l'interet d'avoir un wizard pour ca est de pouvoir imprimer les vignettes directement
def _invoice_labels(self,cr,uid,datas,context):
#   service = netsvc.LocalService("object_proxy")
#   invoice_id = service.execute(uid, 'huissier.vignettes', 'invoice', [datas['id']])
    vign_obj = pooler.get_pool(cr.dbname).get('huissier.vignettes')
    ids = vign_obj.invoice(cr, uid, datas['ids'],context)
    cr.commit()
    print "Facturation finie"
    print "ids",ids
    return{}

def facture(self, cr, uid, data, context):
    id_vignette = pooler.get_pool(cr.dbname).get('huissier.vignettes').browse(cr,uid,data['ids'])
    inv_vignette= id_vignette[0].invoice_id.id or false
    if not inv_vignette: return {}
    return {
        'domain': str([('id', 'in', [inv_vignette])]),
        'name': 'Factures de vignettes en attente',
        'view_type': 'form',
        'view_mode': 'tree,form',
        'res_model': 'account.invoice',
        'view_id': False,
        'type': 'ir.actions.act_window'
    }


class wizard_invoice_labels(wizard.interface):
    states = {
        'init': {
            'actions': [_invoice_labels],
            'result': {'type': 'print', 'report':'huissier.labels', 'state': 'fin'}
        },
        'fin':{
            'actions':[],
            'result':{'type':'action', 'action':facture, 'state':'end'}
        }
    }
wizard_invoice_labels('huissier.labels.invoice')

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

