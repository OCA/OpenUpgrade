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


class sale_order_line(osv.osv):
    _name = 'sale.order.line'
    _description = 'New Sale Order line'
    _inherit = 'sale.order.line'

    def product_id_change(self, cr, uid, ids, pricelist, product, qty=0,
            uom=False, qty_uos=0, uos=False, name='', partner_id=False,
            lang=False, update_tax=True, date_order=False, packaging=False, fiscal_position=False, flag=False):

        result = super(sale_order_line, self).product_id_change(cr, uid, ids,
            pricelist, product, qty, uom, qty_uos, uos, name, partner_id, lang,
            update_tax, date_order, packaging, fiscal_position)

        if not product:
            return {'value': {'price_unit': 0.0, 'notes': '', 'weight': 0}, 'domain': {'product_uom': []}}

        product_res = self.pool.get('product.product').read(cr, uid, [product])[0]

        if product_res['virtual_available'] >= qty and qty != 0.0:
            result['value']['type'] = 'make_to_stock'

        return result

sale_order_line()

