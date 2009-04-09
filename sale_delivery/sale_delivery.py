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

import time
from osv import fields,osv
import netsvc
from mx import DateTime

class sale_delivery_line(osv.osv):
    _name = 'sale.delivery.line'

    _columns = {
        'product_id': fields.many2one('product.product', string='Product', required=True ),
        'product_qty': fields.float('Product Quantity', digits=(16,2), required=True),
        'product_uom' : fields.many2one('product.uom', 'Product UoM', required=True),
        'packaging_id' : fields.many2one('product.packaging', 'Packaging'),
        'date_planned': fields.datetime('Date Planned', select=True, required=True),
        'priority': fields.integer('Priority'),
        'note' : fields.text('Note'),
        'order_id': fields.many2one('sale.order', 'Order Ref', required=True, ondelete='cascade', select=True),
    }
    _order = 'priority,date_planned'
    _defaults = {
        'priority': lambda *a: 1,
    }

    def product_id_change(self, cr, uid, ids, product, qty=0, uom=False, packaging=False):
        warning={}
        product_uom_obj = self.pool.get('product.uom')
        product_obj = self.pool.get('product.product')

        if not product:
            return {'value': {'product_qty' : 0.0, 'product_uom': False,
                'packaging_id': False}, 'domain': {'product_uom': []}}

        result = {}
        product_obj = product_obj.browse(cr, uid, product)
        if packaging:
            default_uom = product_obj.uom_id and product_obj.uom_id.id
            pack = self.pool.get('product.packaging').browse(cr, uid, packaging)
            q = product_uom_obj._compute_qty(cr, uid, uom, pack.qty, default_uom)
            if not (qty % q) == 0 :
                ean = pack.ean
                qty_pack = pack.qty
                type_ul = pack.ul
                warn_msg = "You selected a quantity of %d Units.\nBut it's not compatible with the selected packaging.\nHere is a proposition of quantities according to the packaging: " % (qty)
                warn_msg = warn_msg + "\n\nEAN: " + str(ean) + " Quantiny: " + str(qty_pack) + " Type of ul: " + str(type_ul.name)
                warning={
                    'title':'Packing Information !',
                    'message': warn_msg
                    }
            result['product_qty'] = qty

        result .update({'type': product_obj.procure_method})

        domain = {}
        if not uom:
            result['product_uom'] = product_obj.uom_id.id
            domain = {'product_uom':
                        [('category_id', '=', product_obj.uom_id.category_id.id)],}

        return {'value': result, 'domain': domain,'warning':warning}

sale_delivery_line()


class sale_order(osv.osv):
    _inherit = 'sale.order'
    _columns = {
        'delivery_line': fields.one2many('sale.delivery.line', 'order_id', 'Delivery Lines', readonly=True, states={'draft':[('readonly',False)]}),
    }

    def action_ship_create(self, cr, uid, ids, *args):
        picking = {}
        company = self.pool.get('res.users').browse(cr, uid, uid).company_id
        for order in self.browse(cr, uid, ids, context={}):
            for delivery in order.delivery_line:
                cr.execute('select id from sale_order_line where order_id = %s and product_id = %s',(delivery.order_id.id,delivery.product_id.id))
                if not len(cr.fetchall()):
                    raise osv.except_osv(_('Error !'), _('You have selected a product %s for Delivery but it is not in supposed to be saled in this Sale Order') % (delivery.product_id.name))

            for delivery in order.delivery_line:
                cr.execute('select sum(product_uom_qty) from sale_order_line where order_id = %s and product_id = %s',(delivery.order_id.id,delivery.product_id.id))
                sale_product_qty = cr.fetchall()[0][0] or 0.0
                cr.execute('select sum(product_qty) from sale_delivery_line where order_id = %s and product_id = %s',(delivery.order_id.id,delivery.product_id.id))
                product_qty = cr.fetchall()[0][0]
                if  sale_product_qty != product_qty:
                    raise osv.except_osv(_('Error !'), _('The quanitties plannified in Deliveries must be equals to the quantities in the Sale Order lines. \n\n [%s] %s : %f delivery qty , %f sale order qty' ) % (delivery.product_id.default_code,delivery.product_id.name,product_qty,sale_product_qty))

            location_id = order.shop_id.warehouse_id.lot_stock_id.id
            output_id = order.shop_id.warehouse_id.lot_output_id.id
            if not order.delivery_line:
                return super(sale_order, self).action_ship_create(cr, uid, ids)
            picking_id = False

            for line in order.delivery_line:
                cr.execute('select id from sale_order_line where order_id = %s and product_id = %s',(ids[0],line.product_id.id))
                sale_line_id = cr.fetchall()[0][0]
                sale_line = self.pool.get('sale.order.line').browse(cr, uid, sale_line_id)
                date_planned = line.date_planned
                if line.product_id and line.product_id.product_tmpl_id.type in ('product', 'consu'):
                    if not date_planned in picking:
                        loc_dest_id = order.partner_id.property_stock_customer.id
                        picking_id = self.pool.get('stock.picking').create(cr, uid, {
                            'origin': order.name,
                            'type': 'out',
                            'state': 'confirmed',
                            'move_type': order.picking_policy,
                            'sale_id': order.id,
                            'address_id': order.partner_shipping_id.id,
                            'note': order.note,
                            'invoice_state': (order.order_policy=='picking' and '2binvoiced') or 'none',
                        })
                        picking[date_planned] = picking_id

                    else:
                        picking_id = picking[date_planned]

                    move_id = self.pool.get('stock.move').create(cr, uid, {
                        'name': line.product_id.name[:64],
                        'picking_id': picking_id,
                        'product_id': line.product_id.id,
                        'date_planned': date_planned,
                        'product_qty': line.product_qty,
                        'product_uom': line.product_uom.id,
                        'product_uos_qty': line.product_qty,
                        'product_uos': line.product_uom.id,
                        'product_packaging' : line.packaging_id.id,
                        'address_id' : order.partner_shipping_id.id,
                        'location_id': location_id,
                        'location_dest_id': output_id,
                        'tracking_id': False,
                        'state': 'waiting',
                        'note': line.note,
                    })
                    proc_id = self.pool.get('mrp.procurement').create(cr, uid, {
                        'name': order.name,
                        'origin': order.name,
                        'date_planned': date_planned,
                        'product_id': line.product_id.id,
                        'product_qty': line.product_qty,
                        'product_uom': line.product_uom.id,
                        'product_uos_qty': line.product_qty,
                        'product_uos': line.product_uom.id,
                        'location_id': order.shop_id.warehouse_id.lot_stock_id.id,
                        'procure_method': sale_line.type,
                        'move_id': move_id,
                        'property_ids': [(6, 0, [x.id for x in sale_line.property_ids])],
                    })
                    wf_service = netsvc.LocalService("workflow")
                    wf_service.trg_validate(uid, 'mrp.procurement', proc_id, 'button_confirm', cr)

                elif line.product_id and line.product_id.product_tmpl_id.type=='service':
                    proc_id = self.pool.get('mrp.procurement').create(cr, uid, {
                        'name': line.name,
                        'origin': order.name,
                        'date_planned': date_planned,
                        'product_id': line.product_id.id,
                        'product_qty': line.product_uom_qty,
                        'product_uom': line.product_uom.id,
                        'location_id': order.shop_id.warehouse_id.lot_stock_id.id,
                        'procure_method': line.type,
                        'property_ids': [(6, 0, [x.id for x in line.property_ids])],
                    })
                    wf_service = netsvc.LocalService("workflow")
                    wf_service.trg_validate(uid, 'mrp.procurement', proc_id, 'button_confirm', cr)

                wf_service = netsvc.LocalService("workflow")
                wf_service.trg_validate(uid, 'stock.picking', picking[date_planned], 'button_confirm', cr)

            val = {}

            if order.state=='shipping_except':
                val['state'] = 'progress'
                if (order.order_policy == 'manual') and order.invoice_ids:
                    val['state'] = 'manual'
            self.write(cr, uid, [order.id], val)

        return True
sale_order()

class sale_order_line(osv.osv):
    _inherit = 'sale.order.line'

    def _get_planned_deliveries(self, cr, uid, ids, field_name, arg, context):
        res = {}
        for val in self.browse(cr, uid, ids):
            cr.execute('select sum(product_qty) from sale_delivery_line where order_id = %s and product_id = %s',(val.order_id.id,val.product_id.id))
            product_qty = cr.fetchall()[0][0]
            res[val.id] = product_qty
        return res

    _columns = {
         'deliveries': fields.function(_get_planned_deliveries, method=True, string='Planned Deliveries'),
    }

sale_order_line()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
