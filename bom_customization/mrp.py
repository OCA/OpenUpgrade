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

class mrp_bom(osv.osv):
    _name = 'mrp.bom'
    _inherit = 'mrp.bom'
    
    _columns = { 
        'bom_customizations': fields.many2many('bom_customization.bom_customizations', 'mrp_bom_bom_customizations_rel','bom_id','bom_customization_id', 'BoM Customizations'),
    }
mrp_bom()

class mrp_production(osv.osv):
    _inherit = "mrp.production"
    _name = "mrp.production"
    
    _columns = { 
        'sale_order_line_id': fields.many2one('sale.order.line', 'Related Sale Order Line', readonly=True),
    }
mrp_production()

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
            sale_order_line_id=self.pool.get('sale.order.line').search(cr, uid, [('procurement_id', '=', procurement.id)])
            
            if len(sale_order_line_id)>1:
                print "Something strange going on:"
                print  "len(sale_order_line_id):", len(sale_order_line_id)
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
            ## End Smile's changes
            self.write(cr, uid, [procurement.id], {'state':'running'})
            bom_result = self.pool.get('mrp.production').action_compute(cr, uid,
                    [produce_id], properties=[x.id for x in procurement.property_ids])
            wf_service = netsvc.LocalService("workflow")
            wf_service.trg_validate(uid, 'mrp.production', produce_id, 'button_confirm', cr)
        return produce_id
    
mrp_procurement()