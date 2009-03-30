# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution    
#    Copyright (C) 2009 Smile.fr. All Rights Reserved
#    authors: Raphaël Valyi, Xavier Fernandez
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
from osv import fields, osv

import time
import netsvc
from mx import DateTime

#TODO link this definition to the true one in original mrp/mrp.py
def rounding(f, r):
    if not r:
        return f
    return round(f / r) * r

class mrp_bom(osv.osv):
    _name = 'mrp.bom'
    _inherit = 'mrp.bom'
    
    _columns = { 
        'bom_customization_keys': fields.many2many('bom_customization.bom_customization_keys', 'mrp_bom_bom_customizations_keys_rel', 'bom_id', 'bom_customization_key_id', 'BoM Customizations'),
    }
    
    
    #FIXME do a cleaner overloading with use of super
    def _bom_explode(self, cr, uid, bom, factor, properties, addthis=False, level=0):
        factor = factor / (bom.product_efficiency or 1.0)
        factor = rounding(factor, bom.product_rounding)
        if factor < bom.product_rounding:
            factor = bom.product_rounding
        result = []
        result2 = []
        phantom = False
        if bom.type == 'phantom' and not bom.bom_lines:
            newbom = self._bom_find(cr, uid, bom.product_id.id, bom.product_uom.id, properties)
            if newbom:
                res = self._bom_explode(cr, uid, self.browse(cr, uid, [newbom])[0], factor * bom.product_qty, properties, addthis=True, level=level + 10)
                result = result + res[0]
                result2 = result2 + res[1]
                phantom = True
            else:
                phantom = False
        if not phantom:
            if addthis and not bom.bom_lines:
                result.append(
                {
                    'name': bom.product_id.name,
                    'bom_id': bom.id,
                    'product_id': bom.product_id.id,
                    'product_qty': bom.product_qty * factor,
                    'product_uom': bom.product_uom.id,
                    'product_uos_qty': bom.product_uos and bom.product_uos_qty * factor or False,
                    'product_uos': bom.product_uos and bom.product_uos.id or False,
                })
            if bom.routing_id:
                for wc_use in bom.routing_id.workcenter_lines:
                    wc = wc_use.workcenter_id
                    d, m = divmod(factor, wc_use.workcenter_id.capacity_per_cycle)
                    mult = (d + (m and 1.0 or 0.0))
                    cycle = mult * wc_use.cycle_nbr
                    result2.append({
                        'name': bom.routing_id.name,
                        'workcenter_id': wc.id,
                        'sequence': level + (wc_use.sequence or 0),
                        'cycle': cycle,
                        'hour': float(wc_use.hour_nbr * mult + (wc.time_start + wc.time_stop + cycle * wc.time_cycle) * (wc.time_efficiency or 1.0)),
                    })
            for bom2 in bom.bom_lines:
                res = self._bom_explode(cr, uid, bom2, factor, properties, addthis=True, level=level + 10)
                result = result + res[0]
                result2 = result2 + res[1]
        return result, result2
    
mrp_bom()

class mrp_production(osv.osv):
    _inherit = "mrp.production"
    _name = "mrp.production"
    
    _columns = { 
        'sale_order_line_id': fields.many2one('sale.order.line', 'Related Sale Order Line', readonly=True),
        'dimension_customizations':fields.one2many('sale.order.line.dimension_custom_values', 'mrp_production_id', string="Dimension Custom Values"),

    }
    
    def action_confirm(self, cr, uid, ids):
        super(mrp_production, self).action_confirm(cr, uid, ids)
        for production in self.browse(cr, uid, ids):
            for move_line, product_line in zip(production.move_lines, production.product_lines):
                if move_line.product_id.id != product_line.product_id.id:
                    print "product_id mismatch !"
                else:
                    self.pool.get('stock.move').write(cr, uid, move_line.id, {'bom_id': product_line.bom_id.id})
                    
        
mrp_production()

class mrp_production_product_line(osv.osv):
    _inherit = 'mrp.production.product.line'

    _columns = {
                'bom_id': fields.many2one('mrp.bom', 'Origin bom line'),

    }
mrp_production_product_line()

class mrp_procurement(osv.osv):
    _inherit = 'mrp.procurement'
    _name = 'mrp.procurement'
    
    def action_produce_assign_product(self, cr, uid, ids, context={}):
        print "Overloading successful"
        produce_id = False
        company = self.pool.get('res.users').browse(cr, uid, uid, context).company_id
        for procurement in self.browse(cr, uid, ids):
            res_id = procurement.move_id.id
            loc_id = procurement.location_id.id
            newdate = DateTime.strptime(procurement.date_planned, '%Y-%m-%d %H:%M:%S') - DateTime.RelativeDateTime(days=procurement.product_id.product_tmpl_id.produce_delay or 0.0)
            newdate = newdate - DateTime.RelativeDateTime(days=company.manufacturing_lead)
            
            ## Smile's changes
            ## FIXME sale order line could be copied natively to the production order
            sale_order_line_id = self.pool.get('sale.order.line').search(cr, uid, [('procurement_id', '=', procurement.id)])
            
            if sale_order_line_id:
                 sale_order_line_id = sale_order_line_id[0]
            else:
                 sale_order_line_id = False
            produce_id = self.pool.get('mrp.production').create(cr, uid, {
                'origin': procurement.origin,
                'product_id': procurement.product_id.id,
                'product_qty': procurement.product_qty,
                'product_uom': procurement.product_uom.id,
                'product_uos_qty': procurement.product_uos and procurement.product_uos_qty or False,
                'product_uos': procurement.product_uos and procurement.product_uos.id or False,
                'location_src_id': procurement.location_id.id,
                'location_dest_id': procurement.location_id.id,
                'bom_id': procurement.bom_id and procurement.bom_id.id or False,
                'date_planned': newdate.strftime('%Y-%m-%d %H:%M:%S'),
                'move_prod_id': res_id,
                'sale_order_line_id':sale_order_line_id,
            })
            self.pool.get('sale.order.line').write(cr, uid, sale_order_line_id, {'mrp_production_id': produce_id})
            
            ## End Smile's changes
            self.write(cr, uid, [procurement.id], {'state':'running'})
            bom_result = self.pool.get('mrp.production').action_compute(cr, uid,
                    [produce_id], properties=[x.id for x in procurement.property_ids])
            wf_service = netsvc.LocalService("workflow")
            wf_service.trg_validate(uid, 'mrp.production', produce_id, 'button_confirm', cr)
        return produce_id
    
mrp_procurement()