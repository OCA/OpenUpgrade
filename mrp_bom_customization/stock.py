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


class stock_move(osv.osv):
    _name = 'stock.move'
    _inherit = 'stock.move'
    
    
    def list_customizations(self, cr, uid, ids, name, args, context):
        result = {}
        for id in ids:
            
            result[id] = ""
            
            #TODO CHECKME: stock.move should only be linked to one and only one mrp.production hopefully
            req = """ SELECT sale_order_line_id 
                        FROM mrp_production prod INNER JOIN mrp_production_move_ids rel ON rel.production_id = prod.id
                        WHERE move_id = %d """ % id

            cr.execute(req)
            res = cr.fetchall()

            if not res:
                break
            
            sol_id = res[0][0]
            
            if not sol_id:
#                raise osv.except_osv(_('No sale order line found !'),
#                              _('Save your quotation first.'))
                result[id] = False
                continue
            
            req = """ SELECT cus.customization_key_id, grp.name, val.name 
                        FROM mrp_bom_customization_sale_order_line_customizations cus,
                             mrp_bom_customization_mrp_bom_customization_values val,
                             mrp_bom_customization_mrp_bom_customization_groups grp
                        WHERE cus.sale_order_line_id = %d AND cus.customization_value_id = val.id AND grp.id=val.group_id """ % sol_id
                        
            cr.execute(req)
            res = cr.fetchall()
            
            key_val_grp_dict = dict([(i,(j,k)) for (i,j,k) in res])
            
            
            req = """ SELECT bom_customization_key_id 
                        FROM  mrp_bom_mrp_bom_customizations_keys_rel rel INNER JOIN stock_move sm ON rel.bom_id = sm.bom_id
                        WHERE sm.id = %d """ % id
            cr.execute(req)
            res = cr.fetchall()

            custom_text = ""
            for key in res:
                custom_text+= key_val_grp_dict[key[0]][0] + ":" + key_val_grp_dict[key[0]][1] + ","
            
            if custom_text:
                result[id] = custom_text[0:-1]
            else:
                result[id] = False
            
        return result
        
    
    _columns = { 
        'bom_id': fields.many2one('mrp.bom', 'Origin bom line'),
        'production_orders': fields.many2many('mrp.production', 'mrp_production_move_ids', 'move_id', 'production_id', 'Production Order'),
        'list_customizations': fields.function(list_customizations, string="List of Customizations", method=True, type="char", store=True, size=64, select=True),
    }
stock_move()