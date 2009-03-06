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


class bom_customization_configurator_line(osv.osv_memory):
    _name = "bom_customization.configurator_line"
    
    _columns = {
                'configurator_id': fields.many2one('bom_customization.configurator', 'Configurator'),
                'customization_value_id': fields.many2one('bom_customization.bom_customization_values', 'Customization Value'),
                'customization_key_id': fields.many2one('bom_customization.bom_customization_keys', 'Customization Key'),
                }
bom_customization_configurator_line()


class bom_customization_configurator(osv.osv_memory):
    _name = "bom_customization.configurator"
    
    
    def _list_properties(self, cr, uid, context):
        sol_id = context.get('sol_id', False)
        product_id = self.pool.get('sale.order.line').read(cr, uid, sol_id,['product_id'])['product_id'][0]
        bom_ids = self.pool.get('mrp.bom').search(cr, uid, [('product_id','=',product_id)])
        
        list_property_values= []
        if bom_ids:
            req = """ SELECT rel.property_id, prop.name 
                    FROM mrp_bom_property_rel rel, mrp_property prop 
                    WHERE rel.bom_id IN %s AND prop.id=rel.property_id""" % str(tuple(bom_ids))
            cr.execute(req)
            list_property_values = cr.fetchall()

        return list_property_values
    
    
    _columns = {
                'bom_property_id_selection': fields.selection(_list_properties, "BoM Option", required = True),

                'configurator_line_ids': fields.one2many("bom_customization.configurator_line", 'configurator_id', "Bom Options"),
        
                'product_id': fields.many2one('product.product', "Product", invisible=True),
              }
    
    def default_get(self, cr, uid, fields_list, context=None):
        def_fields = super(osv.osv_memory, self).default_get(cr, uid, fields_list, context)
        
        sol_id = context.get('sol_id', False)
        product_id = self.pool.get('sale.order.line').read(cr, uid, sol_id,['product_id'])['product_id'][0]
        def_fields.update({'product_id':product_id})
        
        return def_fields
    
    def fields_view_get(self, cr, uid, view_id=None, view_type='form', context=None, toolbar=False):
        
        #TODO faire un truc genre ajouter un domain sur le choix de l'organisation des couleurs

        zop = super(osv.osv_memory, self).fields_view_get(cr, uid, view_id, view_type, context, toolbar)
        #print zop
        return zop
        
    def onchange_bom_property_id_selection(self, cr, uid, ids, bom_property_id_selection, product_id):
        req = """ SELECT b.id FROM mrp_bom b, mrp_bom_property_rel rel 
                    WHERE product_id = %d AND rel.bom_id= b.id AND rel.property_id = %d """ % (product_id,bom_property_id_selection)
        cr.execute(req)
        res = cr.fetchall()
        if not res:
            return {'warning': {'title': "Warning", 'message': "No BoM found !"}}
             
        main_bom_id = res[0][0]

        
        bom_ids= self.pool.get('mrp.bom').search(cr, uid, [('bom_id','=',main_bom_id)])
        
        req = """ SELECT DISTINCT c.customization_key_id 
                    FROM bom_customization_bom_customizations c, mrp_bom_bom_customizations_rel rel
                    WHERE rel.bom_id IN %s AND rel.bom_customization_id=c.id """ % str(tuple(bom_ids))
        cr.execute(req)
        keys = cr.fetchall()
        
        line_ids=[]
        for k in keys:
            vals={'customization_key_id':k, 'customization_value_id':None}
            line_ids.append( self.pool.get('bom_customization.configurator_line').create(cr, uid, vals) )
        result={'value':{'configurator_line_ids':line_ids}}
        print result
        return result
        
    def configure_line(self, cr, uid, ids, context={}):
        print "################"
        print "################"
        
    
bom_customization_configurator()