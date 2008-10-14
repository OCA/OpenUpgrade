# -*- encoding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2004-2006 TINY SPRL. (http://tiny.be) All Rights Reserved.
#
# $Id: sale.py 1005 2005-07-25 08:41:42Z nicoe $
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

from osv import fields, osv
from mx import DateTime

class mrp_procurement(osv.osv):
    _inherit = "mrp.procurement"
    _columns = {
        'production_lot_id':fields.many2one('stock.production.lot', 'Production Lot'),
        'customer_ref': fields.char('Customer reference', size=64),
 }

    def action_po_assign(self, cr, uid, ids):
        purchase_id = False

        for procurement in self.browse(cr, uid, ids):
            res_id = procurement.move_id.id
            partner = procurement.product_id.seller_ids[0].name
            partner_id = partner.id
            address_id = self.pool.get('res.partner').address_get(cr, uid, [partner_id], ['delivery'])['delivery']
            pricelist_id = partner.property_product_pricelist_purchase.id

            uom_id = procurement.product_id.uom_po_id.id

            qty = self.pool.get('product.uom')._compute_qty(cr, uid, procurement.product_uom.id, procurement.product_qty, uom_id)
            if procurement.product_id.seller_ids[0].qty:
                qty=max(qty,procurement.product_id.seller_ids[0].qty)

            price = self.pool.get('product.pricelist').price_get(cr, uid, [pricelist_id], procurement.product_id.id, qty, False, {'uom': uom_id})[pricelist_id]

            newdate = DateTime.strptime(procurement.date_planned, '%Y-%m-%d') - DateTime.RelativeDateTime(days=procurement.product_id.product_tmpl_id.seller_delay or 0.0)
            line = {
                'name': procurement.product_id.name[:50],
                'product_qty': qty,
                'product_id': procurement.product_id.id,
                'product_uom': uom_id,
                'price_unit': price,
                'date_planned': newdate.strftime('%Y-%m-%d'),
                'taxes_id': [(6, 0, [x.id for x in procurement.product_id.product_tmpl_id.taxes_id])],
                'move_dest_id': res_id,
                #added
                'production_lot_id': procurement.production_lot_id.id,
                'customer_ref': procurement.customer_ref,
            }
            purchase_id = self.pool.get('purchase.order').create(cr, uid, {
                'origin': procurement.origin,
                'partner_id': partner_id,
                'partner_address_id': address_id,
                'location_id': procurement.location_id.id,
                'pricelist_id': pricelist_id,
                'order_line': [(0,0,line)],
                'invoice_method':'manual',
            })
            self.write(cr, uid, [procurement.id], {'state':'running', 'purchase_id':purchase_id})
        return purchase_id

mrp_procurement()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

