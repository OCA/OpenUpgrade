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

import netsvc
from osv import fields,osv,orm

class delivery_grid(osv.osv):
    _name = "delivery.grid"
    _inherit = "delivery.grid"

    def get_price(self, cr, uid, id, order, dt, context):
        """
        This is not very clean because the function has to check the type of order.
        It could be improve by changing the signature of the method and by passing a dict in place of a browse record.
        """
        total = 0
        weight = 0
        volume = 0

        for line in order.order_line:
            if not line.product_id:
                continue
            qty = 0.0
            
            if order._table_name == "sale.order":
                qty = line.product_uom_qty
            else:
                qty = line.product_qty

            total += line.price_subtotal or 0.0
            weight += (line.product_id.weight or 0.0) * qty
            volume += (line.product_id.volume or 0.0) * qty

        return self.get_price_from_picking(cr, uid, id, total,weight, volume, context)

    def get_price_from_picking(self, cr, uid, id, total, weight, volume, context={}):
        grid = self.browse(cr, uid, id, context)

        price = 0.0
        ok = False

        for line in grid.line_ids:
            price_dict = {'price': total, 'volume':volume, 'weight': weight, 'wv':volume*weight}
            test = eval(line.type+line.operator+str(line.max_value), price_dict)
            if test:
                if context.has_key('object') and context['object']=='purchase':
                    price = line.standard_price
                else:
                    price = line.list_price
                if line.price_type=='variable':
                    price *= price_dict[line.variable_factor]
                ok = True
                break
        if not ok:
            raise except_osv('No price avaible !', 'No line matched this order in the choosed delivery grids !')
        return price

delivery_grid()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

