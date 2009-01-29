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

#
# Dimensions Definition
#
class product_variant_dimension_type(osv.osv):
    _name = "product.variant.dimension.type"
    _description = "Dimension Type"
    _columns = {
        'name' : fields.char('Dimension', size=64),
        'sequence' : fields.integer('Sequence'),
        'value_ids' : fields.one2many('product.variant.dimension.value', 'dimension_id', 'Dimension Values'),
        'product_tmpl_id': fields.many2one('product.template', 'Product Template', required=True),#TODO many2many?
        'allow_custom_value': fields.boolean('Allow Custom Value', help="If true, custom values can be entered in the product configurator"),
    }
    _order = "sequence, name"
product_variant_dimension_type()

class product_variant_dimension_value(osv.osv):
    _name = "product.variant.dimension.value"
    _description = "Dimension Type"
    _columns = {
        'name' : fields.char('Dimension Value', size=64),
        'sequence' : fields.integer('Sequence'),
        'price_extra' : fields.float('Price Extra', size=64),
        'price_margin' : fields.float('Price Margin', size=64),
        'dimension_id' : fields.many2one('product.variant.dimension.type', 'Dimension Type', required=True),
        'product_tmpl_id': fields.related('dimension_id', 'product_tmpl_id', type="many2one", relation="product.template", string="Product Template", store=True),
    }
    _order = "sequence, name"
product_variant_dimension_value()



class product_template(osv.osv):
    _inherit = "product.template"
    
    _columns = {
        'dimension_type_ids':fields.one2many('product.variant.dimension.type', 'product_tmpl_id', 'Dimension Types'),
        'variants':fields.one2many('product.product', 'product_tmpl_id', 'Variants'),
    }
    
product_template()


class product_product(osv.osv):
    _inherit = "product.product"

    def _variant_name_get(self, cr, uid, ids, name, arg, context={}):
        res = {}
        for p in self.browse(cr, uid, ids, context):
            r = map(lambda dim: (dim.dimension_id.name or '')+'/'+(dim.name or '-'), p.dimension_value_ids)
            res[p.id] = ','.join(r)
        return res

    _columns = {
        'dimension_value_ids': fields.many2many('product.variant.dimension.value', 'product_product_dimension_rel', 'product_id','dimension_id', 'Dimensions', domain="[('product_tmpl_id','=',product_tmpl_id)]"),
        'dimension_type_ids': fields.related('product_tmpl_id', 'dimension_type_ids', type="one2many", relation="product.variant.dimension.type", string="Product Template Dimension Types"),
        #
        # TODO: compute price_extra and _margin based on variants
        #
        # 'price_extra': fields.function('Price Extra'),
        # 'price_margin': fields.function('Price Margin'),
        #
        'variants': fields.function(_variant_name_get, method=True, type='char', size=64, string='Variants'),
    }
product_product()


