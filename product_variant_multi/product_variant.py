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
        'sequence' : fields.integer('Sequence', help="The product 'variants' code will use this to order the dimension values"),
        'value_ids' : fields.one2many('product.variant.dimension.value', 'dimension_id', 'Dimension Values'),
        'product_tmpl_id': fields.many2one('product.template', 'Product Template', required=True),
        'allow_custom_value': fields.boolean('Allow Custom Value', help="If true, custom values can be entered in the product configurator"),
    }
    
    _order = "sequence, name"
    
    def name_search(self, cr, user, name='', args=None, operator='ilike', context=None, limit=None):
        if context.get('product_tmpl_id', False):
            return super(product_variant_dimension_type, self).name_search(cr, user, '', args, 'ilike', None, None)
        else:
            return super(product_variant_dimension_type, self).name_search(cr, user, '', None, 'ilike', None, None)
    
product_variant_dimension_type()


class product_variant_dimension_value(osv.osv):
    _name = "product.variant.dimension.value"
    _description = "Dimension Value"
    
    def _get_dimension_values(self, cr, uid, ids, context={}):
        result = []
        for type in self.pool.get('product.variant.dimension.type').browse(cr, uid, ids, context=context):
            for value in type.value_ids:
                result.append(value.id)
        return result
    
    _columns = {
        'name' : fields.char('Dimension Value', size=64, required=True),
        'sequence' : fields.integer('Sequence'),
        'price_extra' : fields.float('Price Extra', size=64),
        'price_margin' : fields.float('Price Margin', size=64),
        'dimension_id' : fields.many2one('product.variant.dimension.type', 'Dimension Type', required=True),
        'product_tmpl_id': fields.related('dimension_id', 'product_tmpl_id', type="many2one", relation="product.template", string="Product Template", store=True),
        'dimension_sequence': fields.related('dimension_id', 'sequence', string="Related Dimension Sequence",#used for ordering purposes in the "variants"
             store={
                'product.variant.dimension.type': (_get_dimension_values, None, 10),
            }),
    }
    _order = "dimension_sequence, sequence, name"
    
product_variant_dimension_value()


class product_template(osv.osv):
    _inherit = "product.template"
    
    _columns = {
        'dimension_type_ids':fields.one2many('product.variant.dimension.type', 'product_tmpl_id', 'Dimension Types'),
        'variant_ids':fields.one2many('product.product', 'product_tmpl_id', 'Variants'),
    }

    def button_generate_variants(self, cr, uid, ids, context={}):
        def cartesian_product(args):
            if len(args) == 1: return [(x,) for x in args[0]]
            return [(i,) + j for j in cartesian_product(args[1:]) for i in args[0]]

        variants_obj = self.pool.get('product.product')
        temp_type_list=[]
        temp_val_list=[]

        for product_temp in self.browse(cr, uid, ids, context):
            for temp_type in product_temp.dimension_type_ids:
                temp_type_list.append(temp_type.id)
                temp_val_list.append([temp_type_value.id for temp_type_value in temp_type.value_ids])
                # if last dimension_type has no dimension_value, we ignore it
                if not temp_val_list[-1]:
                    temp_val_list.pop()
                    temp_type_list.pop()
        
            if temp_val_list:
                list_of_variants = cartesian_product(temp_val_list)
    
                for variant in list_of_variants:
                    constraints_list=[('dimension_value_ids', 'in', [i] ) for i in variant]
                    
                    prod_var=variants_obj.search(cr, uid, constraints_list)
                    if not prod_var:
                        vals={}
                        vals['product_tmpl_id']=product_temp.id
                        vals['dimension_value_ids']=[(6,0,variant)]
    
                        var_id=variants_obj.create(cr, uid, vals, {})

        return True
    
product_template()


class product_product(osv.osv):
    _inherit = "product.product"

    def _variant_name_get(self, cr, uid, ids, name, arg, context={}):
        res = {}
        for product in self.browse(cr, uid, ids, context):
            r = map(lambda dim: (dim.dimension_id.name or '')+':'+(dim.name or '-'), product.dimension_value_ids)
            res[product.id] = ' - '.join(r)
        return res
    
    def _get_products_from_dimension(self, cr, uid, ids, context={}):
        result = []
        for type in self.pool.get('product.variant.dimension.type').browse(cr, uid, ids, context=context):
            for product_id in type.product_tmpl_id.variant_ids:
                result.append(product_id.id)
        return result
    
    def _get_products_from_product(self, cr, uid, ids, context={}):
        result = []
        for product in self.pool.get('product.product').browse(cr, uid, ids, context=context):
            for product_id in product.product_tmpl_id.variant_ids:
                result.append(product_id.id)
        return result

    def _check_dimension_values(self, cr, uid, ids): # TODO: check that all dimension_types of the product_template have a corresponding dimension_value ??
        for p in self.browse(cr, uid, ids, {}):
            buffer = []
            for value in p.dimension_value_ids:
                buffer.append(value.dimension_id)
            unique_set = set(buffer)
            if len(unique_set) != len(buffer):
                return False
        return True
    
    def copy(self, cr, uid, id, default=None, context=None):
        if default is None:
            default = {}
        default = default.copy()
        default.update({'variant_ids':False,})
        return super(product_product, self).copy(cr, uid, id, default, context)

    _columns = {
        'dimension_value_ids': fields.many2many('product.variant.dimension.value', 'product_product_dimension_rel', 'product_id','dimension_id', 'Dimensions', domain="[('product_tmpl_id','=',product_tmpl_id)]"),
        'variants': fields.function(_variant_name_get, method=True, type='char', size=64, string='Variants', readonly=True, 
            store={
                'product.variant.dimension.type': (_get_products_from_dimension, None, 10),
                'product.product': (_get_products_from_product, None, 10),
            }),
    }
    _constraints = [ (_check_dimension_values, 'Several dimension values for the same dimension type', ['dimension_value_ids']),]
    
product_product()
