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

class sale_product_multistep_configurator_configurator_step(osv.osv):
    _inherit = "sale_product_multistep_configurator.configurator.step"
    
    def update_context_before_step(self, cr, user, context={}):
        """Allow to skip the BOM customization wizard if the selected product doesn't have several BOM's"""
        model_list= context.get('step_list', False)
        index = context.get('next_step', 0)
        if index < len(model_list) and model_list[index] == "mrp_bom_customization.configurator":
            sol_id = context.get('sol_id', False)
            if sol_id:
                bom_ids = self.pool.get('mrp.bom').search(cr, user, [('product_id', '=', self.pool.get('sale.order.line').browse(cr, user, sol_id).product_id.id)])
                if (not bom_ids) or len(bom_ids) < 2:
                    context.update({'next_step': index+1 })
        return super(sale_product_multistep_configurator_configurator_step, self).update_context_before_step(cr, user, context)
    
sale_product_multistep_configurator_configurator_step()


class mrp_bom_customization_configurator_line(osv.osv_memory):
    _name = "mrp_bom_customization.configurator_line"
    
    _columns = {
                'configurator_id': fields.many2one('mrp_bom_customization.configurator', 'Configurator'),
                'customization_key_id': fields.many2one('mrp_bom_customization.mrp_bom_customization_keys', 'Customization Key', domain="[('group_id','=', customization_group_id)]"),
                'customization_group_id': fields.many2one('mrp_bom_customization.mrp_bom_customization_groups', 'Customization Group', required=True),
                'customization_value_id': fields.many2one('mrp_bom_customization.mrp_bom_customization_values', 'Customization Value', domain="[('group_id','=', customization_group_id)]"),
                }
    
    def onchange_customization_key_id(self, cr, uid, ids, customization_key_id):
        pass
    
mrp_bom_customization_configurator_line()


class mrp_bom_customization_configurator(osv.osv_memory):
    _name = "mrp_bom_customization.configurator"
    
    def _list_properties(self, cr, uid, context):
        sol_id = context.get('sol_id', False)
        
        if not sol_id:
            raise osv.except_osv(_('No sale order line found in the context !'),
                              _('A product chooser creating a sale order line must be called before this wizard.'))
        
        prod = self.pool.get('sale.order.line').read(cr, uid, sol_id, ['product_id'])['product_id']
        
        if not prod:
            raise osv.except_osv(_('No product found on this sale order line !'),
                              _('A product chooser creating a sale order line must be called before this wizard.'))
        
        product_id = prod[0]
        bom_ids = self.pool.get('mrp.bom').search(cr, uid, [('product_id', '=', product_id)])
        
        list_property_values = []
        if bom_ids:
            req = """ SELECT rel.property_id, prop.name 
                    FROM mrp_bom_property_rel rel, mrp_property prop
                    WHERE rel.bom_id IN %s AND prop.id=rel.property_id """ % ("("+",".join(map(str,bom_ids))+")")
            cr.execute(req)
            list_property_values = cr.fetchall()

        return list_property_values
    
    
    _columns = {
                'bom_property_id_selection': fields.selection(_list_properties, "BoM Option"),
                'configurator_line_ids': fields.one2many("mrp_bom_customization.configurator_line", 'configurator_id', "Bom Options"),
                'product_id': fields.many2one('product.product', "Product", invisible=True),
                'property_mrp_bom_customization_main_property_group': fields.property('mrp.property.group',
                        type='many2one',
                        relation='mrp.property.group',
                        string="BoM customization property",
                        method=True,
                        view_load=True,
                        domain="[]",
                        help="Test",
                        required=True),
              }
    
    def default_get(self, cr, uid, fields_list, context=None):
        def_fields = super(osv.osv_memory, self).default_get(cr, uid, fields_list, context)
        
        sol_id = context.get('sol_id', False)
        
        product_id = self.pool.get('sale.order.line').read(cr, uid, sol_id, ['product_id'])['product_id'][0]

        def_fields.update({'product_id':product_id})
        
        
        if context.get('active_id_object_type', False) == 'sale.order.line':
            property_ids = self.pool.get('sale.order.line').read(cr, uid, sol_id, ['property_ids'])['property_ids']
            
            for property in self._list_properties(cr, uid, context):
                for prop_id in property_ids:
                    if prop_id == property[0]:
                        def_fields.update({'bom_property_id_selection':prop_id})
        return def_fields
    
    def get_property_groups(self, cr, uid, ids, bom_property_id_selection, product_id, sol_id):
        # product_id is not defined, thus active_id_object_type equals sale.order.line and this wizard is modifying an existing
        # sale.order.line, default_values have to be loaded
        load_values_from_sol = False
        if not product_id:
            product_id = self.pool.get('sale.order.line').read(cr, uid, sol_id, ['product_id'])['product_id'][0]
            load_values_from_sol = True
            
        
        req = """ SELECT b.id FROM mrp_bom b, mrp_bom_property_rel rel 
                    WHERE product_id = %d AND rel.bom_id= b.id AND rel.property_id = %d """ % (product_id, bom_property_id_selection)
        cr.execute(req)
        res = cr.fetchall()
        if not res:
            return {'warning': {'title': "Warning", 'message': "No BoM found !"}}
             
        main_bom_id = res[0][0]
        bom_ids = self.pool.get('mrp.bom').search(cr, uid, [('bom_id', '=', main_bom_id)])
        
        req = """ SELECT DISTINCT mrp_bom_customization_key_id
                    FROM mrp_bom_mrp_bom_customizations_keys_rel
                    WHERE bom_id IN %s """ % str(tuple(bom_ids))
        cr.execute(req)
        keys = cr.fetchall()
        
        group_ids = self.pool.get('mrp_bom_customization.mrp_bom_customization_keys').read(cr, uid, [k[0] for k in keys], ['group_id'])
        return load_values_from_sol, keys, group_ids
        
    def onchange_bom_property_id_selection(self, cr, uid, ids, bom_property_id_selection, product_id, sol_id):

        load_values_from_sol, keys, group_ids = self.get_property_groups(cr, uid, ids, bom_property_id_selection, product_id, sol_id)
        
        line_ids = []
        lines_to_remove = []
        
        if ids:
            if self.read(cr, uid, ids, ['configurator_line_ids'])[0]:
                new_lines = [id for id in self.read(cr, uid, ids, ['configurator_line_ids'])[0]['configurator_line_ids']]
                if len(line_ids) == len(group_ids):
                    line_ids.append(new_lines)
                    return {'value':{'configurator_line_ids':line_ids}}
                else:
                    self.pool.get('mrp_bom_customization.configurator_line').unlink(cr, uid, new_lines)
                    cr.commit()
        
        for k, g in zip(keys, group_ids):
            vals = {'customization_key_id': k[0], 'customization_value_id':None, 'customization_group_id':g['group_id']}
            if load_values_from_sol:
                sol_custom_obj = self.pool.get('mrp_bom_customization.sale_order_line_customizations')
                customization_ids = sol_custom_obj.search(cr, uid, [('sale_order_line_id', '=', sol_id), ('customization_key_id', '=', k[0])])
                if customization_ids:
                    vals['customization_value_id'] = sol_custom_obj.read(cr, uid, customization_ids[0], ['customization_value_id'])['customization_value_id']
            if ids:
                vals.update({'configurator_id': ids[0]})
            
            line_ids.append(self.pool.get('mrp_bom_customization.configurator_line').create(cr, uid, vals))

        return {'value':{'configurator_line_ids':line_ids}}
    
    def onchange_configurator_line_ids(self, cr, uid, ids, configurator_line_ids, bom_property_id_selection, product_id):
        pass
    
    def create(self, cr, uid, vals, context=None):
        id = super(osv.osv_memory, self).create(cr, uid, vals, context)
        line_ids = [i[1] for i in vals['configurator_line_ids']]
        if line_ids:
            self.pool.get('mrp_bom_customization.configurator_line').write(cr, uid, line_ids, {'configurator_id':id})
        return id
        
    def configure_line(self, cr, uid, ids, context={}):
        res = self.read(cr, uid, ids, ['bom_property_id_selection', 'configurator_line_ids'])[0]
        sol_id = context.get('sol_id', False)
        
        if len(self._list_properties(cr, uid, context)) == 0:
            return self.pool.get('sale_product_multistep_configurator.configurator.step').next_step(cr, uid, context)
        
        if not res['bom_property_id_selection'] or not sol_id:
            return False
        
        load_values_from_sol, keys, group_ids = self.get_property_groups(cr, uid, ids, res['bom_property_id_selection'], context.get('product_id', False), sol_id)
        if len(group_ids) != len(res['configurator_line_ids']):
            return False

        for line in self.pool.get('mrp_bom_customization.configurator_line').read(cr, uid, res['configurator_line_ids']):
            if (not line['customization_key_id']) or not line['customization_value_id']:
                return False
        
        self.pool.get('sale.order.line').write(cr, uid, sol_id, {'property_ids': [(6, 0, [res['bom_property_id_selection']])] })
        
        if context.get('active_id_object_type', False) == 'sale.order.line':
            for line in self.pool.get('mrp_bom_customization.configurator_line').read(cr, uid, res['configurator_line_ids']):
                customization_ids = self.pool.get('mrp_bom_customization.sale_order_line_customizations').search(cr, uid, [('sale_order_line_id', '=', sol_id), ('customization_key_id', '=', line['customization_key_id'])])
                if customization_ids:
                    self.pool.get('mrp_bom_customization.sale_order_line_customizations').write(cr, uid, customization_ids[0], {'customization_value_id': line['customization_value_id']})
                else:
                    vals = {
                          'sale_order_line_id': sol_id,
                          'customization_value_id': line['customization_value_id'],
                          'customization_key_id': line['customization_key_id'],
                        }
                    self.pool.get('mrp_bom_customization.sale_order_line_customizations').create(cr, uid, vals)
        else:
            for line in self.pool.get('mrp_bom_customization.configurator_line').read(cr, uid, res['configurator_line_ids']):
                vals = {
                      'sale_order_line_id': sol_id,
                      'customization_value_id': line['customization_value_id'],
                      'customization_key_id': line['customization_key_id'],
                    }
                self.pool.get('mrp_bom_customization.sale_order_line_customizations').create(cr, uid, vals)
            
        return self.pool.get('sale_product_multistep_configurator.configurator.step').next_step(cr, uid, context)
    
    def _check_selection(self, cr, uid, ids):
        for configurator in self.browse(cr, uid, ids):
            if len(self._list_properties(cr, uid, {})) and not configurator.bom_property_id_selection:
                return False
        return True
    
    
#    _constraints = [ (_check_selection, 'Error ! Choose a bom customization.', ['bom_property_id_selection']) ]
           
mrp_bom_customization_configurator()