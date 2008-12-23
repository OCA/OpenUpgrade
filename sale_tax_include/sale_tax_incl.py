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
import ir

class sale_order(osv.osv):
    _inherit = "sale.order"
    def _amount_line_tax(self, cr, uid, line, context={}):
        return line.price_subtotal_incl - line.price_subtotal
    _columns = {
        'price_type': fields.selection([
            ('tax_included','Tax included'),
            ('tax_excluded','Tax excluded')
        ], 'Price method', required=True),
    }
    _defaults = {
        'price_type': lambda *a: 'tax_excluded',
    }
    def _inv_get(self, cr, uid, order, context={}):
        return {
            'price_type': order.price_type
        }
sale_order()

class sale_order_line(osv.osv):
    _inherit = "sale.order.line"
    def _amount_line2(self, cr, uid, ids, name, args, context={}):
        """
        Return the subtotal excluding taxes with respect to price_type.
        """
        res = {}
        tax_obj = self.pool.get('account.tax')
        res_init = super(sale_order_line, self)._amount_line(cr, uid, ids, name, args, context)
        for line in self.browse(cr, uid, ids):
            res[line.id] = {
                'price_subtotal': 0.0,
                'price_subtotal_incl': 0.0,
                'data': []
            }
            if not line.product_uom_qty:
                continue
            if line.order_id:
                product_taxes = []
                if line.product_id:
                    product_taxes = filter(lambda x: x.price_include, line.product_id.taxes_id)

                if ((set(product_taxes) == set(line.tax_id)) or not product_taxes) and (line.order_id.price_type == 'tax_included'):
                    res[line.id]['price_subtotal_incl'] = res_init[line.id]
                else:
                    res[line.id]['price_subtotal'] = res_init[line.id]
                    for tax in tax_obj.compute_inv(cr, uid, product_taxes, res_init[line.id]/line.product_uom_qty, line.product_uom_qty):
                        res[line.id]['price_subtotal'] = res[line.id]['price_subtotal'] - round(tax['amount'], 2)
            else:
                res[line.id]['price_subtotal'] = res_init[line.id]

            if res[line.id]['price_subtotal']:
                res[line.id]['price_subtotal_incl'] = res[line.id]['price_subtotal']
                for tax in tax_obj.compute(cr, uid, line.tax_id, res[line.id]['price_subtotal']/line.product_uom_qty, line.product_uom_qty):
                    res[line.id]['price_subtotal_incl'] = res[line.id]['price_subtotal_incl'] + tax['amount']
                    res[line.id]['data'].append( tax)
            else:
                res[line.id]['price_subtotal'] = res[line.id]['price_subtotal_incl']
                for tax in tax_obj.compute_inv(cr, uid, line.tax_id, res[line.id]['price_subtotal_incl']/line.product_uom_qty, line.product_uom_qty):
                    res[line.id]['price_subtotal'] = res[line.id]['price_subtotal'] - tax['amount']
                    res[line.id]['data'].append( tax)

        res[line.id]['price_subtotal']= round(res[line.id]['price_subtotal'], 2)
        res[line.id]['price_subtotal_incl']= round(res[line.id]['price_subtotal_incl'], 2)
        return res

    def _get_order(self, cr, uid, ids, context):
        result = {}
        for inv in self.pool.get('sale.order').browse(cr, uid, ids, context=context):
            for line in inv.order_line:
                result[line.id] = True
        return result.keys()
    _columns = {
        'price_subtotal': fields.function(_amount_line2, method=True, string='Subtotal w/o tax', multi='amount',
            store={'sale.order':(_get_order,['price_type'],-2), 'sale.order.line': (lambda self,cr,uid,ids,c={}: ids, None,-2)}),
        'price_subtotal_incl': fields.function(_amount_line2, method=True, string='Subtotal', multi='amount',
            store={'sale.order':(_get_order,['price_type'],-2), 'sale.order.line': (lambda self,cr,uid,ids,c={}: ids, None,-2)}),
    }
sale_order_line()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

