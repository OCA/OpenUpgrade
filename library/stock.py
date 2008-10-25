# -*- encoding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2006 TINY SPRL. (http://tiny.be) All Rights Reserved.
#                    Fabien Pinckaers <fp@tiny.Be>
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsability of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# garantees and support are strongly adviced to contract a Free Software
# Service Company
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
##############################################################################

from osv import osv, fields
import time
import netsvc

class stock_move(osv.osv):
    _inherit = 'stock.move'
    _columns = {
        'customer_ref': fields.char('Customer reference', size=64),
        'procurement_ids': fields.one2many('mrp.procurement','move_id', 'Procurements')
    }


    # New function to manage the update of the quantities
    def onchange_qty(self, cr, uid, ids, qty, context=None):
        return {'value': {'product_uos_qty':qty,'product_qty':qty}}



    # action_cancel overidden to avoid the cascading cancellation
    def action_cancel(self, cr, uid, ids, context={}):
        if not len(ids):
            return True
        pickings = {}
        for move in self.browse(cr, uid, ids):
            if move.state in ('confirmed','waiting','assigned','draft'):
                if move.picking_id:
                    pickings[move.picking_id.id] = True
        self.write(cr, uid, ids, {'state':'cancel'})
        for pick_id in pickings:
            wf_service = netsvc.LocalService("workflow")
            wf_service.trg_validate(uid, 'stock.picking', pick_id, 'button_cancel', cr)
        ids2 = []
        for res in self.read(cr, uid, ids, ['move_dest_id']):
            if res['move_dest_id']:
                ids2.append(res['move_dest_id'][0])

        wf_service = netsvc.LocalService("workflow")
        for id in ids:
            wf_service.trg_trigger(uid, 'stock.move', id, cr)
        #self.action_cancel(cr,uid, ids2, context) # $$ [removed to avoid cascading cancellation]
        return True

stock_move()

class stock_picking(osv.osv):
    _inherit = 'stock.picking'
    _order = "create_date desc"
    _columns = {
        'sale_id': fields.many2one('sale.order', 'Sale Order', ondelete='set null', select=True, readonly=True),
        'purchase_id': fields.many2one('purchase.order', 'Purchase Order', ondelete='set null', readonly=True,select=True),
        'date_done': fields.datetime('Picking date', readonly=True),
    }
    _defaults = {
        'sale_id': lambda *a: False,
        'purchase_id': lambda *a: False,
    }
stock_picking()


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

