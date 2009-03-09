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

from osv import fields,osv
import tools
import ir
import pooler

import netsvc
import time
from mx import DateTime

#
#Development for Partner
#Also include the link between the production and procurement
#

class mrp_production(osv.osv):
    _name = 'mrp.production'
    _inherit='mrp.production'
    _columns={
        'partner_id':fields.many2one('res.partner', 'Partner',  select=True),
        'procure_id': fields.many2one('mrp.procurement', 'Procurement', readonly=True),
        'note': fields.text('Notes'),
          }

    def action_confirm(self, cr, uid, ids):
        picking_id=False
        proc=self.pool.get('mrp.procurement')
        for production in self.browse(cr, uid, ids):
            picking_id=super(mrp_production, self).action_confirm(cr,uid,[production.id])
            move_ids = self.pool.get('stock.move').search(cr, uid, [('picking_id','=',picking_id)])
            for move_id in move_ids:
                proc_ids = proc.search(cr,uid,[('move_id','=',move_id)])

                proc.write(cr, uid, proc_ids, {'partner_id': production.partner_id.id})
        return picking_id
mrp_production()

class sale_order(osv.osv):
    _name="sale.order"
    _inherit="sale.order"

    def action_ship_create(self, cr, uid, ids, *args):
        super(sale_order, self).action_ship_create(cr,uid,ids,*args)
        proc=self.pool.get('mrp.procurement')
        for order in self.browse(cr, uid, ids, context={}):
            for line in order.order_line:
                proc.write(cr, uid, [line.procurement_id.id], {'partner_id': order.partner_id.id})
        return True

sale_order()
class mrp_procurement(osv.osv):
    _name = "mrp.procurement"
    _inherit="mrp.procurement"
    _columns={
        'partner_id':fields.many2one('res.partner', 'Partner',  select=True),

          }

    def action_produce_assign_product(self, cr, uid, ids, context={}):
        produce_id = False
        for procurement in self.browse(cr, uid, ids):
            res_id = procurement.move_id.id
            loc_id = procurement.location_id.id
            newdate = DateTime.strptime(procurement.date_planned, '%Y-%m-%d %H:%M:%S') - DateTime.RelativeDateTime(days=procurement.product_id.product_tmpl_id.produce_delay or 0.0)
            produce_id = self.pool.get('mrp.production').create(cr, uid, {
                'origin': procurement.origin,
                'product_id': procurement.product_id.id,
                'product_qty': procurement.product_qty,
                'product_uom': procurement.product_uom.id,
                'location_src_id': procurement.location_id.id,
                'location_dest_id': procurement.location_id.id,
                'date_planned': newdate,
                'move_prod_id': res_id,
                'partner_id': procurement.partner_id.id,
                'procure_id':procurement.id,
            })
            self.write(cr, uid, [procurement.id], {'state':'running'})
            bom_result = self.pool.get('mrp.production').action_compute(cr, uid,
                    [produce_id], properties=[x.id for x in procurement.property_ids])
            wf_service = netsvc.LocalService("workflow")
            wf_service.trg_validate(uid, 'mrp.production', produce_id, 'button_confirm', cr)
        return produce_id
mrp_procurement()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

