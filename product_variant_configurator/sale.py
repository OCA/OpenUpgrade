# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution    
#    Copyright (C) 2009 Smile.fr. All Rights Reserved
#    authors: Raphaël Valyi, Xavier Fernandez
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


class sale_order_line_dimension_custom_values(osv.osv):
    _name = "sale.order.line.dimension_custom_values"
    
    def _get_to_update_ids(self, cr, uid, ids, context={}):
        result = []
        for sol in self.pool.get('sale.order.line').browse(cr, uid, ids, context=context):
            for d_c_value in sol.dimension_custom_value_ids:
                result.append(d_c_value.id)
        return result
    
    _columns = {
                "dimension_type_id": fields.many2one("product.variant.dimension.type", "Dimension Type"),
                "custom_value": fields.char('Custom Value', size=64),
                "sale_order_line_id": fields.many2one("sale.order.line", "Sale Order Line"),
                "mrp_production_id": fields.related('sale_order_line_id', 'mrp_production_id', type="many2one", relation="mrp.production", string="Production Order",
                                        store={
                                               'sale.order.line': (_get_to_update_ids, None, 10),
                                               }),
                }
    
sale_order_line_dimension_custom_values()


class sale_order_line(osv.osv):
    _inherit = "sale.order.line"
    
    _columns = {
                "dimension_custom_value_ids": fields.one2many('sale.order.line.dimension_custom_values', 'sale_order_line_id', 'Dimension Custom Values'),
                }
    
sale_order_line()