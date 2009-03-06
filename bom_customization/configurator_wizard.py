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



class bom_customization_configurator(osv.osv_memory):
    _name = "bom_customization.configurator"
    
    _columns = {
                #TODO wrong def form demo!!!!
                'bom_property_id': fields.many2one('mrp.property', "BoM Option", required = True),
                'bom_key_values': fields.one2many("bom_customization.bom_customization_values", 'group_id', "Bom Options"),
              }
    
    def fields_view_get(self, cr, uid, view_id=None, view_type='form', context=None, toolbar=False):
        sol_id = context.get('sol_id', False)
        product_id = self.pool.get('sale.order.line').read(cr, uid, sol_id,['product_id'])['product_id'][0]        
        bom_ids = self.pool.get('mrp.bom').search(cr, uid, [('product_id','=',product_id)])
        
        list_property_values= []
        if bom_ids:
            req = """ SELECT property_id FROM mrp_bom_property_rel WHERE bom_id IN %s """ % str(tuple(bom_ids))
            cr.execute(req)
            list_property_values = cr.fetchall()
        
            #TODO faire un truc genre ajouter un domain sur le choix de l'organisation des couleurs
        

        zop = super(osv.osv_memory, self).fields_view_get(cr, uid, view_id, view_type, context, toolbar)
        print zop
        return zop
        
    def onchange_bom_property(self, cr, uid, ids, bom_property_id):
        pass
        #d'une maniere ou d'une autre on connait la bonne bom: bom_id
        req = """ SELECT DISTINCT customization_key_id FROM bom_customization_bom_customizations WHERE bom_id = %d """ % (bom_id,)
        cr.execute(req)
        keys = cr.fetchall()
        
    
bom_customization_configurator()