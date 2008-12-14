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
import pooler
import netsvc

class stock_heatcode(osv.osv):
    _name = 'product.lot.foundry.heatcode'
    _description = "Heat Code"
    _columns = {
        'name': fields.char('Heat Code', size=64, required=True),
        'date': fields.date('Date', required=True),
        'chemical_ids': fields.one2many('product.lot.foundry.heatcode.chemical', 'heatcode_id', 'Chemical Properties'),
        'mecanical_ids': fields.one2many('product.lot.foundry.heatcode.mecanical', 'heatcode_id','Mecanical Properties'),
        'lot_ids': fields.one2many('stock.production.lot', 'heatcode_id','Lots'),
        'state': fields.selection([
            ('draft','Draft'),
            ('valid','Valid')
        ], 'State', required=True)
    }
    _defaults = {
        'date': lambda *args: time.strftime('%Y-%m-%d'),
        'state': lambda *args: 'draft'
    }
    def name_get(self, cr, uid, ids, context={}):
        res = {}
        for lot in self.browse(cr, uid, ids, context):
            res[lot.id] = lot.name+'   '
            for prop in lot.chemical_ids:
                res[lot.id]+= (' %s=<%s>' % (prop.name,prop.value))
        return res.items()
stock_heatcode()


class stock_heatcode_mecanical(osv.osv):
    _name = 'product.lot.foundry.heatcode.mecanical'
    _description = "Mecanical Properties"
    _columns = {
        'name': fields.char('Property', size=64, required=True),
        'value': fields.char('Value', size=64, required=True),
        'heatcode_id': fields.many2one('product.lot.foundry.heatcode', 'Heatcode'),
    }
stock_heatcode_mecanical()


class stock_heatcode_chemical(osv.osv):
    _name = 'product.lot.foundry.heatcode.chemical'
    _description = "Chemical Properties"
    _columns = {
        'name': fields.char('Property', size=64, required=True),
        'value': fields.char('Value', size=64, required=True),
        'heatcode_id': fields.many2one('product.lot.foundry.heatcode', 'Heatcode'),
    }
stock_heatcode_chemical()



class stock_production_lot(osv.osv):
    _name = 'stock.production.lot'
    _inherit = 'stock.production.lot'
    def _available_get(self, cr, uid, ids, name, args, context={}):
        res = {}
        for lot in self.browse(cr, uid, ids, context):
            if lot.type=='bar':
                x = lot.size_x
                for res2 in lot.reservation_ids:
                    x -= res2.size_x
                print  ('%.2f mm'% (x,)), res

                res[lot.id] = ('%.2f mm'% (x,))
            else:
                res[lot.id] = '%d mm x 122mm x 12mm\n%d mm x 22mm x 12mm' % (lot.size_x or 0.0,lot.size_x or 0.0)
        return res
    def _get_size(dtype):
        def calc_date(self, cr, uid, context={}):
            if context.get('product_id', False):
                product = pooler.get_pool(cr.dbname).get('product.product').browse(cr, uid, [context['product_id']])[0]
                duree = getattr(product, dtype) or 0
                return duree
            else:
                return False
        return calc_date

    _columns = {
        'size_x': fields.float('Width'),
        'size_y': fields.float('Length'),
        'size_z': fields.float('Thickness'),
        'product_id': fields.many2one('product.product', 'Product'),
        'heatcode_id': fields.many2one('product.lot.foundry.heatcode', 'Heatcode'),
        'type': fields.selection([
            ('bar','Bar'),
            ('plate','Plate')
        ], 'Type', required=True),
        'status': fields.selection([
            ('draft', 'Draft'),
            ('valid', 'Valid'),
            ('non conformity', 'Non Conformity'),
            ('done', 'Done')
        ], 'Status', required=True),
        'quality_info': fields.text('Quality Information'),
        'reservation_ids': fields.one2many('stock.production.lot.reservation', 'lot_id', 'Reservations'),
        'available': fields.function(_available_get, type="text", method=True, string='Availables'),
    }
    _defaults = {
        'status': lambda *args: 'draft',
        'product_id': lambda self,cr, uid, ctx: ctx.get('product_id', False),
        'name': lambda *args: time.strftime('%Y-%m-%d'),
        'type': lambda *args: 'bar',
        'size_x': _get_size('Width'),
        'size_y': _get_size('Length'),
        'size_z': _get_size('Thickness'),
    }
stock_production_lot()

class stock_production_lot_reservation(osv.osv):
    _name = 'stock.production.lot.reservation'
    _columns = {
        'name': fields.char('Reservation', size=64),
        'date': fields.date('Date'),
        'size_x': fields.float('Width'),
        'size_y': fields.float('Length'),
        'size_z': fields.float('Thickness'),
        'lot_id': fields.many2one('stock.production.lot', 'Lot', required=True, ondelete="cascade")
    }
    _defaults = {
        'date': lambda *args: time.strftime('%Y-%m-%d'),
    }
stock_production_lot_reservation()

class product_product(osv.osv):
    _inherit = 'product.product'
    _columns = {
        'size_x': fields.float('Width'),
        'size_y': fields.float('Length'),
        'size_z': fields.float('Thickness'),
        'lot_ids': fields.one2many('stock.production.lot', 'product_id', 'Lots'),
        'cutting': fields.boolean('Can be Cutted'),
        'auto_picking': fields.boolean('Auto Picking for Production')
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
                    cr.execute('update stock_move set location_id=%s where id=%s', (move.product_id.property_stock_production.id, move.id))

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
                        cr.execute('update stock_move set location_id=%s, product_qty=%s where id=%s', (r[1],r[0], move.id))

                        while res:
                            r = res.pop(0)
                            move_id = self.copy(cr, uid, move.id, {'product_qty':r[0], 'location_id':r[1]})
                            done.append(move_id)
                            #cr.execute('insert into stock_move_history_ids values (%s,%s)', (move.id,move_id))
        if done:
            count += len(done)
            self.write(cr, uid, done, {'state':'assigned'})

        if count:
            for pick_id in pickings:
                wf_service = netsvc.LocalService("workflow")
                wf_service.trg_write(uid, 'stock.picking', pick_id, cr)
        return count

stock_move()


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

