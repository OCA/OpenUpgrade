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

class product_product(osv.osv):
    _name = "product.template"
    _inherit = "product.template"

    _columns = {
        'x': fields.float('X of Product'),
        'y': fields.float('Y of Product'),
        'z': fields.float('Z of Product'),
        'cutting': fields.boolean('Can be Cutted'),
        'auto_picking': fields.boolean('Auto Picking for Production'),
    }
product_product()


class stock_move(osv.osv):
    _inherit = "stock.move"
    def check_assign(self, cr, uid, ids, context={}):
        done = []
        count=0
        pickings = {}
        for move in self.browse(cr, uid, ids):
            if move.product_id.type == 'consu':
                if mode.state in ('confirmed', 'waiting'):
                    done.append(move.id)
                pickings[move.picking_id.id] = 1
                continue
            if move.state in ('confirmed','waiting'):
                if move.product_id.cutting:
                    # TODO Check for reservation
                    done.append(move.id)
                    pickings[move.picking_id.id] = 1
                    cr.execute('update stock_move set location_id=%d where id=%d', (move.product_id.property_stock_production_id.id, move.id))

                    move_id = self.copy(cr, uid, move.id, {
                        'product_uos_qty': move.product_uos_qty,
                        'product_qty': 0,
                        'location_id': move.location_id.id,
                        'location_dest_id': move.product_id.property_stock_production.id
                    })
                    done.append(move_id)

                else:
                    res = self.pool.get('stock.location')._product_reserve(cr, uid, [move.location_id.id], move.product_id.id, move.product_qty, {'uom': move.product_uom.id})
                    if res:
                        done.append(move.id)
                        pickings[move.picking_id.id] = 1
                        r = res.pop(0)
                        cr.execute('update stock_move set location_id=%d, product_qty=%f where id=%d', (r[1],r[0], move.id))

                        while res:
                            r = res.pop(0)
                            move_id = self.copy(cr, uid, move.id, {'product_qty':r[0], 'location_id':r[1]})
                            done.append(move_id)
                            #cr.execute('insert into stock_move_history_ids values (%d,%d)', (move.id,move_id))
        if done:
            count += len(done)
            self.write(cr, uid, done, {'state':'assigned'})

        if count:
            for pick_id in pickings:
                wf_service = netsvc.LocalService("workflow")
                wf_service.trg_write(uid, 'stock.picking', pick_id, cr)
        return count

stock_move()



class sale_order_line(osv.osv):
    _name = "sale.order.line"
    _inherit = "sale.order.line"
    _columns = {
        'x': fields.float('X of Product'),
        'y': fields.float('Y of Product'),
        'z': fields.float('Z of Product')
    }

    def product_id_change(self, cr, uid, ids, pricelist, product, qty=0,
            uom=False,weight=0, qty_uos=0, uos=False, name='', partner_id=False,
            lang=False, update_tax=True):

        datas = super(sale_order_line,self).product_id_change(cr, uid, ids, pricelist, product, qty=0,uom=False,qty_uos=0, uos=False, name='', partner_id=False,
            lang=False, update_tax=True)
        if qty:
            datas['value']['th_weight'] = weight * qty
        else:
            datas['value']['th_weight'] = weight * qty_uos
        return datas
sale_order_line()


#class stock_production_lot(osv.osv):
#    _name = 'stock.production.lot'
#    _inherit = 'stock.production.lot'
#    _columns = {
#        'x': fields.float('X of Product'),
#        'y': fields.float('Y of Product'),
#        'z': fields.float('Z of Product'),
#        #'heatcode_id' :  fields.many2one('product.heatcode','Heatcode'),
#	}
##Quality information
##Localisation
##Reservations (one2many qty, sizes)
##Availables (computed field)
#
#
#stock_production_lot()




# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

