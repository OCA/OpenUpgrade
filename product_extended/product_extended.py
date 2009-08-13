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

from osv import fields
from osv import osv
import ir
import pooler

class product_supplierinfo(osv.osv):
    _inherit = 'product.supplierinfo'
    _name = "product.supplierinfo"

    def _last_order(self, cr, uid, ids, name, arg, context):
        res = {}
        for supinfo in self.browse(cr, uid, ids):
            cr.execute("select po.id, max(po.date_approve) from purchase_order as po, purchase_order_line as line where po.id=line.order_id and product_id=%s and partner_id=%s and state='approved' group by po.id", (supinfo.product_id.id, supinfo.name.id,))
            record = cr.fetchone()
            if record:
                res[supinfo.id] = record[0]
            else:
                res[supinfo.id] = False
        return res

    def _last_order_date(self, cr, uid, ids, name, arg, context):
        res = {}
        po = self.pool.get('purchase.order')
        last_orders = self._last_order(cr, uid, ids, name, arg, context)
        dates = po.read(cr, uid, filter(None, last_orders.values()), ['date_approve'])
        for suppinfo in ids:
            date_approve = [x['date_approve'] for x in dates if x['id']==last_orders[suppinfo]]
            if date_approve:
                res[suppinfo] = date_approve[0]
            else:
                res[suppinfo] = False
        return res

    _columns = {
        'last_order' : fields.function(_last_order, type='many2one', obj='purchase.order', method=True, string='Last Order'),
        'last_order_date' : fields.function(_last_order_date, type='date', method=True, string='Last Order date'),
    }
product_supplierinfo()


class product_product(osv.osv):
    _name = 'product.product'
    _inherit = 'product.product'
    
    def _find_op(self, cr, uid, ids, name, arg, context):
        res = {}
        for product_id in ids:
            cr.execute('SELECT swo.id from stock_warehouse_orderpoint AS swo WHERE product_id=%s', (product_id,))
            op_id = cr.fetchone()
            if op_id:
                res[product_id] = op_id[0]
            else:
                res[product_id] = False
        return res

    #def _product_dispo(self, cr, uid, ids, name, arg, context={}):
        #res = {}
        #out = self._product_outgoing_qty(cr, uid, ids, name, arg, context)
        #now = self._product_qty_available(cr, uid, ids, name, arg, context)
        #for p_id in ids:
            #res[p_id] = now[p_id] + out[p_id]
        #return res


    _columns = {
        'calculate_price': fields.boolean('Compute standard price', help="Check this box if the standard price must be computed from the BoM."),
        'orderpoint_ids': fields.one2many('stock.warehouse.orderpoint', 'product_id', 'Orderpoints'),
        #'qty_dispo': fields.function(_product_dispo, method=True, type='float', string='Stock available'),
    }

    _defaults = {
        'calculate_price': lambda w,x,y,z: False,
    }

    def compute_price(self, cr, uid, ids, *args):
        for prod_id in ids:
            bom_ids = pooler.get_pool(cr.dbname).get('mrp.bom').search(cr, uid, [('product_id', '=', prod_id)])
            if bom_ids:
                for bom in pooler.get_pool(cr.dbname).get('mrp.bom').browse(cr, uid, bom_ids):
                    self._calc_price(cr, uid, bom)
        return True
                    
    def _calc_price(self, cr, uid, bom):
        if not bom.product_id.calculate_price:
            return bom.product_id.standard_price
        else:
            price = 0
            if bom.bom_lines:
                for sbom in bom.bom_lines:
                    price += self._calc_price(cr, uid, sbom) * sbom.product_qty                    
            else:
                bom_obj = pooler.get_pool(cr.dbname).get('mrp.bom')
                no_child_bom = bom_obj.search(cr, uid, [('product_id', '=', bom.product_id.id), ('bom_id', '=', False)])
                if no_child_bom and bom.id not in no_child_bom:
                    other_bom = bom_obj.browse(cr, uid, no_child_bom)[0]
                    if not other_bom.product_id.calculate_price:
                        price += self._calc_price(cr, uid, other_bom) * other_bom.product_qty
                    else:
#                        price += other_bom.product_qty * other_bom.product_id.standard_price
                        price += other_bom.product_id.standard_price
                else:
#                    price += bom.product_qty * bom.product_id.standard_price
                    price += bom.product_id.standard_price
#                if no_child_bom:
#                    other_bom = bom_obj.browse(cr, uid, no_child_bom)[0]
#                    price += bom.product_qty * self._calc_price(cr, uid, other_bom)
#                else:
#                    price += bom.product_qty * bom.product_id.standard_price
            if bom.routing_id:
                for wline in bom.routing_id.workcenter_lines:
                    wc = wline.workcenter_id
                    cycle = wline.cycle_nbr
                    hour = (wc.time_start + wc.time_stop + cycle * wc.time_cycle) *  (wc.time_efficiency or 1.0)
                    price += wc.costs_cycle * cycle + wc.costs_hour * hour
                    price = self.pool.get('product.uom')._compute_price(cr,uid,bom.product_uom.id,price,bom.product_id.uom_id.id)
            if bom.bom_lines:
                self.write(cr, uid, [bom.product_id.id], {'standard_price' : price/bom.product_qty})
            if bom.product_uom.id != bom.product_id.uom_id.id:
                price = self.pool.get('product.uom')._compute_price(cr,uid,bom.product_uom.id,price,bom.product_id.uom_id.id)
            return price
product_product()

class product_bom(osv.osv):
    _inherit = 'mrp.bom'
            
    _columns = {
        'standard_price': fields.related('product_id','standard_price',type="float",relation="product.product",string="Standard Price",store=False)
    }

product_bom()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

