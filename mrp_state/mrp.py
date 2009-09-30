

from osv import fields
from osv import osv
import ir

import netsvc
import time
from mx import DateTime
from tools.translate import _

class mrp_flow(osv.osv):
    '''
    Open ERP Model
    '''
    _inherit = 'mrp.production'
    
    def action_confirm(self, cr, uid, ids):
        picking_id=False
        proc_ids = []
        for production in self.browse(cr, uid, ids):
            if not production.product_lines:
                self.action_compute(cr, uid, [production.id])
                production = self.browse(cr, uid, [production.id])[0]
            routing_loc = None
            pick_type = 'internal'
            address_id = False
            if production.bom_id.routing_id and production.bom_id.routing_id.location_id:
                routing_loc = production.bom_id.routing_id.location_id
                if routing_loc.usage<>'internal':
                    pick_type = 'out'
                address_id = routing_loc.address_id and routing_loc.address_id.id or False
                routing_loc = routing_loc.id
            picking_id = self.pool.get('stock.picking').create(cr, uid, {
                'origin': (production.origin or '').split(':')[0] +':'+production.name,
                'type': pick_type,
                'move_type': 'one',
                'state': 'auto',
                'address_id': address_id,
                'auto_picking': self._get_auto_picking(cr, uid, production),
            })

            source = production.product_id.product_tmpl_id.property_stock_production.id
            data = {
                'name':'PROD:'+production.name,
                'date_planned': production.date_planned,
                'product_id': production.product_id.id,
                'product_qty': production.product_qty,
                'product_uom': production.product_uom.id,
                'product_uos_qty': production.product_uos and production.product_uos_qty or False,
                'product_uos': production.product_uos and production.product_uos.id or False,
                'location_id': source,
                'location_dest_id': production.location_dest_id.id,
                'move_dest_id': production.move_prod_id.id,
                'state': 'waiting'
            }
            res_final_id = self.pool.get('stock.move').create(cr, uid, data)

            self.write(cr, uid, [production.id], {'move_created_ids': [(6, 0, [res_final_id])]})
            moves = []
            states = []
            for line in production.product_lines:
                move_id=False
                newdate = production.date_planned
                if line.product_id.type in ('product', 'consu'):
                    res_dest_id = self.pool.get('stock.move').create(cr, uid, {
                        'name':'PROD:'+production.name,
                        'date_planned': production.date_planned,
                        'product_id': line.product_id.id,
                        'product_qty': line.product_qty,
                        'product_uom': line.product_uom.id,
                        'product_uos_qty': line.product_uos and line.product_uos_qty or False,
                        'product_uos': line.product_uos and line.product_uos.id or False,
                        'location_id': routing_loc or production.location_src_id.id,
                        'location_dest_id': source,
                        'move_dest_id': res_final_id,
                        'state': 'waiting',
                    })
                    moves.append(res_dest_id)
                    move_id = self.pool.get('stock.move').create(cr, uid, {
                        'name':'PROD:'+production.name,
                        'picking_id':picking_id,
                        'product_id': line.product_id.id,
                        'product_qty': line.product_qty,
                        'product_uom': line.product_uom.id,
                        'product_uos_qty': line.product_uos and line.product_uos_qty or False,
                        'product_uos': line.product_uos and line.product_uos.id or False,
                        'date_planned': newdate,
                        'move_dest_id': res_dest_id,
                        'location_id': production.location_src_id.id,
                        'location_dest_id': routing_loc or production.location_src_id.id,
                        'state': 'waiting',
                    })
                    states.append((res_dest_id, move_id))
                proc_id = self.pool.get('mrp.procurement').create(cr, uid, {
                    'name': (production.origin or '').split(':')[0] + ':' + production.name,
                    'origin': (production.origin or '').split(':')[0] + ':' + production.name,
                    'date_planned': newdate,
                    'product_id': line.product_id.id,
                    'product_qty': line.product_qty,
                    'product_uom': line.product_uom.id,
                    'product_uos_qty': line.product_uos and line.product_qty or False,
                    'product_uos': line.product_uos and line.product_uos.id or False,
                    'location_id': production.location_src_id.id,
                    'procure_method': line.product_id.procure_method,
                    'move_id': move_id,
                })
                wf_service = netsvc.LocalService("workflow")
                wf_service.trg_validate(uid, 'mrp.procurement', proc_id, 'button_confirm', cr)
                proc_ids.append(proc_id)
            wf_service = netsvc.LocalService("workflow")
            wf_service.trg_validate(uid, 'stock.picking', picking_id, 'button_confirm', cr)
            self.write(cr, uid, [production.id], {'picking_id':picking_id, 'move_lines': [(6,0,moves)], 'state':'confirmed'})
        for state in states:
            sts = self.pool.get('stock.move').browse(cr, uid, state[1]).state
            self.pool.get('stock.move').write(cr, uid, state[0], {'state':sts})

        return picking_id
    
    def _check_states(self, cr, uid, ids=False, context={}):
        result = True
        move_pool = self.pool.get('stock.move')
        
        if not ids:
            ids = self.search(cr, uid, [('state','=','confirmed')])
            
        for po in self.browse(cr, uid, ids):
            for line in po.move_lines:
                id = move_pool.search(cr, uid, [('picking_id','=',po.picking_id.id),('product_id','=',line.product_id.id)])
                state = move_pool.browse(cr, uid, id)[0].state
                if state == 'confirmed':
                    state = 'waiting'
                move_pool.write(cr, uid, [line.id], {'state':state})
        cr.commit()
        return result
mrp_flow()

class mrp_procurement(osv.osv):
    _inherit = 'mrp.procurement'

    def _procure_confirm(self, cr, uid, ids=None, use_new_cursor=False, context=None):
        res = super(mrp_procurement, self)._procure_confirm(cr, uid, ids, use_new_cursor, context)
        self.pool.get('mrp.production')._check_states(cr, uid, context=context)
        return res
        
mrp_procurement()
