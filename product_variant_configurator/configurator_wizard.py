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


class product_variant_configurator_line(osv.osv_memory):
    _name = "product_variant_configurator.line"

    _columns = {
                "dimension_type_id": fields.many2one('product.variant.dimension.type', "Dimension Type", domain="[('product_tmpl_id','=',product_tmpl_id)]"),
                "dimension_type_value_id": fields.many2one('product.variant.dimension.value',"Dimension Value", domain="[('dimension_id','=',dimension_type_id)]"),
                "dimension_custom_value": fields.char('Custom Value', size=64),
                "configurator_test_id": fields.many2one('product_variant_configurator.configurator', 'product_variant_configurator Test', required=True),
                "modified": fields.boolean('Is Modified?', invisible=True),
                #"product_tmpl_id": fields.related('configurator_test_id','product_tmpl_id', type="many2one", relation="product.template", string="Product Template")
    }
    
    def onchange_dimension_type_value_id(self, cr, uid, ids, dimension_type_value_id):
        return {'value':{'dimension_type_value_id':dimension_type_value_id, 'modified':True}}
    
    def onchange_dimension_custom_value(self, cr, uid, ids, dimension_custom_value):
        return {'value':{'dimension_custom_value':dimension_custom_value, 'modified':True}}

product_variant_configurator_line()

class product_variant_configurator_configurator(osv.osv_memory):
    _name = "product_variant_configurator.configurator"
    #TODO rename
    
    _columns={
              "product_tmpl_id": fields.many2one('product.template', "Product Template"),
              "dimension_configuration_line_ids": fields.one2many('product_variant_configurator.line', 'configurator_test_id', 'Configurator Lines'),
              "product_variant_id": fields.many2one('product.product', "Product Variant", domain="[('product_tmpl_id','=',product_tmpl_id)]"),
              "next_step": fields.char('Next Step', size=64),
    }
    _defaults = {
                 "next_step": lambda self, cr, uid, context : context.get('next_step', False),
                 }
    
    #TODO load the product of the sale order line in the wizard in case of modification
    
#    def default_get(self, cr, uid, fields, form=None, reference=None):

#        if not (form.get('active_id_object_type',False)=='sale.order.line' and form.get('active_id',False)):
#            return super(osv.osv_memory,self).default_get(cr, uid, fields, form, reference)
#        
#        sol_id = form.get('active_id')
#        res = self.pool.get('sale.order.line').read(cr,uid,[sol_id])[0]
#        
#        vals={'product_variant_id':res['product_id'],}
#        
#        return vals
    
    def onchange_product_tmpl_id(self, cr, uid, ids, product_tmpl_id=False):
        result = {}
        if not product_tmpl_id:
            return result
        
        #print "product_tmpl_id:", product_tmpl_id
        product_template = self.pool.get('product.template').browse(cr, uid, product_tmpl_id)
        dim_ids = product_template.dimension_type_ids
        
        line_ids = []
        for dim in dim_ids:
            value_ids = self.pool.get('product.variant.dimension.value').search(cr, uid, [('dimension_id', '=', dim.id)])
            
            if value_ids:
                vals = {'dimension_type_id':dim.id, 'dimension_type_value_id':None}#value_ids[0]
                line_ids.append(self.pool.get('product_variant_configurator.line').create(cr, uid, vals))

        result['value'] = {'dimension_configuration_line_ids': line_ids}
        return result
    
    def onchange_product_variant_id(self, cr, uid, ids, product_variant_id=False, dimension_configuration_line_ids=False):
        result = {}
        if not product_variant_id:
            return result
        
        line_obj = self.pool.get('product_variant_configurator.line')
        
        dim_value_ids = self.pool.get('product.product').read(cr,uid,product_variant_id)['dimension_value_ids']
        dim_couple= [(dim_id,self.pool.get('product.variant.dimension.value').read(cr,uid,dim_id)['dimension_id']) for dim_id in dim_value_ids]
#        
        for line in dimension_configuration_line_ids:
            for couple in dim_couple:
                if line[2]['dimension_type_id'] == couple[1][0]:
                    vals={'dimension_type_value_id':couple[0], 'dimension_custom_value':line[2]['dimension_custom_value'], 'modified': True}
                    line_obj.write(cr, uid, [line[1]], vals)

        line_ids = [line[1] for line in dimension_configuration_line_ids]

        result['value'] = {'dimension_configuration_line_ids': line_ids}
        
        return result

    
    def configure_line(self, cr, uid, ids, context={}):
        print context
        
        active_id_object_type = context.get('active_id_object_type', False)
        res_obj = self.pool.get('sale.order.line')
        sol_id = False
        
        
        if active_id_object_type == 'sale.order':
            print "Creating Line"
            
            order_id = context.get('active_id', False)
            
            for res in self.read(cr,uid,ids):
                if res['product_tmpl_id']:
                    tmpl_obj=self.pool.get('product.template')
                    tmpl_infos=tmpl_obj.read(cr,uid,res['product_tmpl_id'],['name','uom_id'])
                    default_uom_id=tmpl_infos['uom_id'][0]
                    tmpl_name=tmpl_infos['name']

                    if res['product_variant_id']:
                        prod_name=self.pool.get('product.product').read(cr,uid,res['product_variant_id'])['variants']
                        vals = {'order_id':order_id,
                              'product_id':res['product_variant_id'],
                              'delay':0.0,
                              'name': tmpl_name + " - " + prod_name,
                              'type':'make_to_order',
                              'state':'draft',
                              'price_unit':0.0,
                              'product_uom_qty':1.0,
                              'product_uom':default_uom_id,}          
                        print res
                        
                        print "vals new object:",vals
                        
                        if res['product_variant_id']: sol_id = res_obj.create(cr, uid, vals, context=context)
        
        elif active_id_object_type == 'sale.order.line':
            print "Modifying Line"
            
            sol_id = context.get('active_id', False)
            print "sol_id",sol_id
            
            for res in self.read(cr,uid,ids):
                if res['product_tmpl_id']:
                    default_uom_id = self.pool.get('product.template').read(cr,uid,res['product_tmpl_id'])['uom_id'][0]
                    if res['product_variant_id']:
                        prod_name = self.pool.get('product.product').read(cr,uid,res['product_variant_id'])['variants']
                        vals = {'product_id':res['product_variant_id'],'name':prod_name,}
                        print "vals", vals
                        if res['product_variant_id']: res_obj.write(cr, uid, [sol_id], vals)
            
        
        if sol_id and active_id_object_type == 'sale.order':
            
            #TODO inherit this response from generic configurator
            return {
                    'view_type': 'form',
                    "view_mode": 'form',
                    'res_model': context.get('next_step', False),#'sale_product_multistep_configurator', #'ir.actions.configuration.wizard',
                    'type': 'ir.actions.act_window',
                    'target':'new',
                }
            
        elif active_id_object_type == 'sale.order.line':
            return {
                    'type': 'ir.actions.act_window_close',
            }
        else:
            return True
        
product_variant_configurator_configurator()
