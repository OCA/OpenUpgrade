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

from osv import fields, osv

class sale_order(osv.osv):
    _name = "sale.order"
    _inherit = "sale.order"
    _defaults = {
        'name': lambda obj, cr, uid, context: obj.pool.get('sale.order').so_seq_get(cr, uid),
              }
    def copy(self, cr, uid, id, default=None,context={}):
        name=self.so_seq_get(cr, uid)
        if not default:
            default = {}
        default.update({
            'state':'draft',
            'shipped':False,
            'invoice_ids':[],
            'picking_ids':[],
            'name': name,
        })
        return super(osv.osv, self).copy(cr, uid, id, default, context)
    def so_seq_get(self, cr, uid):

        pool_seq=self.pool.get('ir.sequence')
        seq_ids = pool_seq.search(cr, uid, [('code','=','sale.order')])
        res = pool_seq.read(cr, uid, seq_ids)[0]
        if res:
            if res['number_next']:
                return pool_seq._process(res['prefix']) + '%%0%sd' % res['padding'] % res['number_next'] + pool_seq._process(res['suffix'])
            else:
                return pool_seq._process(res['prefix']) + pool_seq._process(res['suffix'])
        return False

    def create(self, cr, user, vals, context=None):
        name=self.pool.get('ir.sequence').get(cr, user, 'sale.order')
        return super(sale_order,self).create(cr, user, vals, context)

sale_order()

class purchase_order(osv.osv):
    _name = "purchase.order"
    _inherit = "purchase.order"
    _defaults = {
        'name': lambda obj, cr, uid, context: obj.pool.get('purchase.order').po_seq_get(cr, uid),
        }

    def copy(self, cr, uid, id, default=None,context={}):
        name=self.po_seq_get(cr, uid)
        if not default:
            default = {}
        default.update({
            'state':'draft',
            'shipped':False,
            'invoice_ids':[],
            'picking_ids':[],
            'name': name,
        })
        return super(osv.osv, self).copy(cr, uid, id, default, context)

    def po_seq_get(self, cr, uid):

        pool_seq=self.pool.get('ir.sequence')
        seq_ids = pool_seq.search(cr, uid, [('code','=','purchase.order')])
        res = pool_seq.read(cr, uid, seq_ids)[0]
        if res:
            if res['number_next']:
                return pool_seq._process(res['prefix']) + '%%0%sd' % res['padding'] % res['number_next'] + pool_seq._process(res['suffix'])
            else:
                return pool_seq._process(res['prefix']) + pool_seq._process(res['suffix'])
        return False

    def create(self, cr, user, vals, context=None):
        name=self.pool.get('ir.sequence').get(cr, user, 'purchase.order')
        return super(purchase_order,self).create(cr, user, vals, context)

purchase_order()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

