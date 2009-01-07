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
import netsvc
from osv import fields, osv

class product_index(osv.osv):
    def _current_rate(self, cr, uid, ids, name, arg, context={}):
        res={}
        date = context.get('date', time.strftime('%Y-%m-%d'))
        for id in ids:
            cr.execute("SELECT index_id, rate FROM product_index_rate WHERE index_id = %s AND name <= '%s' ORDER BY name desc LIMIT 1" % (id, date))
            if cr.rowcount:
                id, rate=cr.fetchall()[0]
                res[id]=rate
            else:
                res[id]=0
        return res
    _name = "product.index"
    _description = "Index"
    _columns = {
        'name': fields.char('Index name', size=32, required=True),
        'code': fields.char('Index code', size=3),
        'rate': fields.function(_current_rate, method=True, string='Current rate',digits=(12,6)),
        'rate_ids': fields.one2many('product.index.rate', 'index_id', 'Rates'),
        'rounding': fields.float('Rounding factor', digits=(12,6)),
        'active': fields.boolean('Active'),
    }
    _sql_constraints = [
        ('rounding_zero', 'CHECK (rounding>0)',  'The rounding must be > 0 !')
    ]
    _order = 'name'
    _defaults = {
        'active': lambda *a: 1,
    }
    _order = "code"

    def round(self, cr, uid, index, amount, context={}):
        return round(amount / index.rounding) * index.rounding

    def compute(self, cr, uid, index, amount, date_from, date_to=None, round=True, context={}):
        if not date_to:
            date_to = time.strftime('%Y-%m-%d')
        cr.execute('select rate from product_index_rate where name<=%s and index_id=%s order by name desc limit 1', (date_from, index.id))
        ifrom = cr.rowcount and cr.fetchone()[0] or 1.0
        cr.execute('select rate from product_index_rate where name<=%s and index_id=%s order by name desc limit 1', (date_to, index.id))
        ito = cr.rowcount and cr.fetchone()[0] or 1.0
        val = amount * ito / ifrom
        if round:
            val = self.round(cr, uid, index, val)
        return val
product_index()

class product_index_rate(osv.osv):
    _name = "product.index.rate"
    _description = "Index Rate"
    _columns = {
        'name': fields.date('Date', required=True, select=True),
        'rate': fields.float('Rate', digits=(12,6), required=True),
        'index_id': fields.many2one('product.index', 'index', readonly=True),
    }
    _defaults = {
        'name': lambda *a: time.strftime('%Y-%m-%d'),
    }
    _order = "name desc"
product_index_rate()


class product_index(osv.osv):
    _inherit = 'product.product'
    def _current_rate(self, cr, uid, ids, name, arg, context={}):
        res=dict(map(lambda x: (x,0.0), ids))
        if not name [-6:]=='_index':
            raise 'The field name should end by _index !'
        fname = name[:-6]
        for product in self.browse(cr, uid, ids, context):
            val = getattr(product, fname)
            if fname in ('list_price',):
                ifields = product.index_sale
            else:
                ifields = product.index_purchase
            for i in ifields:
                val = self.pool.get('product.index').compute(cr, uid, i, val, product.index_date)
            res[product.id] = val
        return res
    _columns = {
        'buyer_price':fields.float('Buyer price'),
        'index_sale': fields.many2many('product.index', 'product_index_sale_rel', 'product_id', 'index_id', 'Sales indexes'),
        'index_purchase': fields.many2many('product.index', 'product_index_purchase_rel', 'product_id', 'index_id', 'Purchase indexes'),

        'index_date': fields.date('Index price date', required=True),

        'list_price_index': fields.function(_current_rate, method=True, string='Indexed list price',digits=(12,6)),
        'standard_price_index': fields.function(_current_rate, method=True, string='Indexed standard price',digits=(12,6)),
        'buyer_price_index': fields.function(_current_rate, method=True, string='Indexed buyer price',digits=(12,6)),
    }
    _defaults = {
        'buyer_price': lambda *args: 0.0,
        'index_date': lambda *args: time.strftime('%Y-%m-%d')
    }
product_index()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

