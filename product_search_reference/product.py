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
from osv import osv, fields


class Product(osv.osv):
    _inherit = 'product.product'

    def _partner_ref2(self, cursor, user, ids, name, arg, context=None):
        res = {}
        for product in self.browse(cursor, user, ids, context=context):
            res[product.id] = '\n'.join([x.product_code \
                    for x in product.seller_ids if x.product_code]) or ''
        return res

    def _partner_ref2_search(self, cursor, user, obj, name, args):
        supplierinfo_obj = self.pool.get('product.supplierinfo')
        args = args[:]
        i = 0
        while i < len(args):
            args[i] = ('product_code', args[i][1], args[i][2])
            i += 1
        supplierinfo_ids = supplierinfo_obj.search(cursor, user, args)
        product_ids = [ x.product_id.id for x in supplierinfo_obj.browse(cursor, user,
                supplierinfo_ids) if x.product_id]
        return [('id', 'in', product_ids)]

    _columns = {
        'partner_ref2': fields.function(_partner_ref2, method=True,
            type='char', string='Customer ref', fnct_search=_partner_ref2_search,
            select=2),
    }

    def name_search(self, cursor, user, name='', args=None, operator='ilike',
            context=None, limit=80):
        ids = self.search(cursor, user, [('partner_ref2', '=', name)] + args,
                limit=limit, context=context)
        if ids:
            return self.name_get(cursor, user, ids, context=context)
        return super(Product, self).name_search(cursor, user, name=name, args=args,
                operator=operator, context=context, limit=limit)

Product()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

