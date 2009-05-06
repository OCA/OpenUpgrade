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

from mx import DateTime
import netsvc
from osv import fields, osv


class sale_order_line(osv.osv):
    _inherit = 'sale.order.line'
    _columns = {
        'production_lot_id': fields.many2one('stock.production.lot', 'Production Lot',),
        'customer_ref': fields.char('Customer reference', size=64),
    }

    _defaults = {
        'type': lambda *a: 'make_to_order',
        }

    def button_confirm(self, cr, uid, ids, context={}):
        lines = self.pool.get('sale.order.line').browse(cr, uid, ids)
        l_id = 0
        for line in lines:
            if line.production_lot_id:
                continue
            l_id += 1
            production_lot_dico = {
                'name': line.order_id and (str(line.order_id.name)+('/%02d'%(l_id,))) or False,
                'product_id': line.product_id.id
            }
            production_lot_id = self.pool.get('stock.production.lot').create(cr, uid, production_lot_dico)
            self.pool.get('sale.order.line').write(cr, uid, [line.id], {'production_lot_id': production_lot_id})

        super(sale_order_line, self).button_confirm(cr, uid, ids, context)
        return

    def copy(self, cr, uid, id, default=None, context={}):
        if not default:
            default = {}
        default.update({
            'production_lot_id': False,
            'customer_ref': ''
        })
        return super(sale_order_line, self).copy(cr, uid, id, default, context)
sale_order_line()


class sale_order(osv.osv):

    _inherit = "sale.order"
    _order = "create_date desc"

    _defaults = {
        'invoice_quantity': lambda *a: 'procurement',
        'picking_policy': lambda *a: 'direct',
        'order_policy': lambda *a: 'picking',
    }

    def action_ship_create(self, cr, uid, ids, *args):
        picking_id = False
        for order in self.browse(cr, uid, ids, context={}):
            output_id = order.shop_id.warehouse_id.lot_output_id.id
            picking_id = False
            for line in order.order_line:
                proc_id = False
                date_planned = (DateTime.now() + DateTime.RelativeDateTime(days=line.delay or 0.0)).strftime('%Y-%m-%d')
                if line.state == 'done':
                    continue
                if line.product_id and line.product_id.product_tmpl_id.type in ('product', 'consu'):
                    location_id = order.shop_id.warehouse_id.lot_stock_id.id
                    if not picking_id:
                        loc_dest_id = order.partner_id.property_stock_customer.id
                        picking_id = self.pool.get('stock.picking').create(cr, uid, {
                            'origin': order.name,
                            'type': 'out',
                            'state': 'auto',
                            'move_type': order.picking_policy,
                            'sale_id': order.id,
                            'address_id': order.partner_shipping_id.id,
                            'note': order.note,
                            'invoice_state': (order.order_policy=='picking' and '2binvoiced') or 'none',
                            'carrier_id': order.carrier_id.id,
                        })
                    move_id = self.pool.get('stock.move').create(cr, uid, {
                        'name': 'SO:' + order.name,
                        'picking_id': picking_id,
                        'product_id': line.product_id.id,
                        'date_planned': date_planned,
                        'product_qty': line.product_uom_qty,
                        'product_uom': line.product_uom.id,
                        'product_uos_qty': line.product_uos_qty,
                        'product_uos': line.product_uos.id,
                        'product_packaging': line.product_packaging.id,
                        'address_id': line.address_allotment_id.id or order.partner_shipping_id.id,
                        'location_id': location_id,
                        'location_dest_id': output_id,
                        'sale_line_id': line.id,
                        'tracking_id': False,
                        'state': 'waiting',
                        'note': line.notes,
                        'prodlot_id': line.production_lot_id.id,
                        'customer_ref': line.customer_ref,
                    })
                    proc_id = self.pool.get('mrp.procurement').create(cr, uid, {
                        'name': order.name,
                        'origin': order.name,
                        'date_planned': date_planned,
                        'product_id': line.product_id.id,
                        'product_qty': line.product_uom_qty,
                        'product_uom': line.product_uom.id,
                        'location_id': order.shop_id.warehouse_id.lot_stock_id.id,
                        'procure_method': line.type,
                        'move_id': move_id,
                        'production_lot_id': line.production_lot_id.id,
                        'customer_ref': line.customer_ref,
                    })
                    wf_service = netsvc.LocalService("workflow")
                    wf_service.trg_validate(uid, 'mrp.procurement', proc_id, 'button_confirm', cr)
                    self.pool.get('sale.order.line').write(cr, uid, [line.id], {'procurement_id': proc_id})
                elif line.product_id and line.product_id.product_tmpl_id.type == 'service':
                    proc_id = self.pool.get('mrp.procurement').create(cr, uid, {
                        'name': line.name,
                        'origin': order.name,
                        'date_planned': date_planned,
                        'product_id': line.product_id.id,
                        'product_qty': line.product_uom_qty,
                        'product_uom': line.product_uom.id,
                        'location_id': order.shop_id.warehouse_id.lot_stock_id.id,
                        'procure_method': line.type,
                    })
                    wf_service = netsvc.LocalService("workflow")
                    wf_service.trg_validate(uid, 'mrp.procurement', proc_id, 'button_confirm', cr)
                    self.pool.get('sale.order.line').write(cr, uid, [line.id], {'procurement_id': proc_id})
                else:
                    #
                    # No procurement because no product in the sale.order.line.
                    #
                    pass

            val = {}
            if picking_id:
                wf_service = netsvc.LocalService("workflow")
                wf_service.trg_validate(uid, 'stock.picking', picking_id, 'button_confirm', cr)
                #val = {'picking_ids':[(6,0,[picking_id])]}

            if order.state == 'shipping_except':
                val['state'] = 'progress'
                if (order.order_policy == 'manual') and order.invoice_ids:
                    val['state'] = 'manual'
            self.write(cr, uid, [order.id], val)
        return True



#   def action_ship_create(self, cr, uid, ids, *args):
#       result = super(sale_order, self).action_ship_create(cr, uid, ids, *args)
#       mids=[]
#       pids=[]
#       move_obj = self.pool.get('stock.move')
#       proc_obj = self.pool.get('mrp.procurement')
#       for order in self.browse(cr, uid, ids, context={}):
#           for line in order.order_line:
#               for move in line.move_ids :
#                   mids.append(move.id)
#                   pids.extend([p.id for p in move.procurement_ids])
#               move_obj.write(cr, uid, mids, {
#                   'prodlot_id': line.production_lot_id.id,
#                   'customer_ref': line.customer_ref
#               })
#               proc_obj.write(cr, uid, pids, {
#                   'production_lot_id': line.production_lot_id.id,
#                   'customer_ref': line.customer_ref
#               })

#       return result

sale_order()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

