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
    
    _columns = {
                "dimension_type_id": fields.many2one("product.variant.dimension.type", "Dimension Type"),
                "custom_value": fields.char('Custom Value', size=64),
                "sale_order_line_id": fields.many2one("sale.order.line", "Sale Order Line"),
                }
    
sale_order_line_dimension_custom_values()


class sale_order_line(osv.osv):
    _inherit = "sale.order.line"
    
    _columns = {
                "dimension_custom_value_ids": fields.one2many('sale.order.line.dimension_custom_values', 'sale_order_line_id', 'Dimension Custom Values'),
                }
    
sale_order_line()