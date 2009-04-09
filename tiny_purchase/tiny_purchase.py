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

from osv import osv
from osv import fields
import time


class product(osv.osv):
    _name = "tiny_purchase.product"
    _columns = {
        'name': fields.char('Name', size=64),
        'price': fields.float('Price'),
    }
product()

class order(osv.osv):
    _name = "tiny_purchase.order"

    _columns = {
        'name': fields.date('Date'),
        'user_id': fields.many2one('res.users', 'User', required=True),
        'line_ids': fields.one2many('tiny_purchase.line', 'order_id', 'Lines'),
        'state': fields.selection([('draft', 'Draft'), ('confirmed', 'Confirmed'), ('done', 'Done')], 'State'),
    }

    _defaults = {
        'name': lambda *a: time.strftime('%Y-%m-%d'),
        'user_id': lambda self, cr, uid, context: uid,
        'state': lambda *a: 'draft',
    }
order()

class line(osv.osv):
    _name = "tiny_purchase.line"
    _rec_name = "product_id"

    def _get_price(self, cr, uid, ids, field_name=None, arg=None, context={}):
        res={}
        lines=self.browse(cr, uid, ids)
        for l in lines:
            if l.product_id:
                res[l.id]=l.quantity * l.product_id.price
            else:
                res[l.id]=0
        return res

    _columns = {
        'product_id': fields.many2one('tiny_purchase.product', 'Product', required=True),
        'quantity': fields.integer('Quantity'),
        'price': fields.function(_get_price, method=True, string='Price', type='float'),
        'comments': fields.text('Comments'),
        'order_id': fields.many2one('tiny_purchase.order', 'Order', required=True),
    }

    _defaults = {
        'quantity': lambda *a: 0,
    }

    def onchange_compute_price(self, cr, uid, ids, product_id, quantity):
        if not product_id:
            return {}
        price = self.pool.get('tiny_purchase.product').read(cr, uid, [product_id], ['price'])[0]['price']
        return {'value':{'price': price * quantity,}}
line()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

