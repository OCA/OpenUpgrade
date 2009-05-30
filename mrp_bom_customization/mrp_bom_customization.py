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

class mrp_bom_customization_groups(osv.osv):
    _name = "mrp_bom_customization.mrp_bom_customization_groups"
    
    _columns = {
                'name': fields.char('Group Name', size=64, select=1),
                'key_ids': fields.one2many("mrp_bom_customization.mrp_bom_customization_keys", 'group_id', "Keys"),
                'value_ids': fields.one2many("mrp_bom_customization.mrp_bom_customization_values", 'group_id', "Values"),
    }
mrp_bom_customization_groups()

class mrp_bom_customization_keys(osv.osv):
    _name = "mrp_bom_customization.mrp_bom_customization_keys"
    
    _columns = {
                'name': fields.char('Key Name', size=64, select=1),
                'group_id': fields.many2one('mrp_bom_customization.mrp_bom_customization_groups', "Customization Group", required = True),
    }
mrp_bom_customization_keys()

class mrp_bom_customization_values(osv.osv):
    _name = "mrp_bom_customization.mrp_bom_customization_values"
    
    _columns = {
                'name': fields.char('Value Name', size=64, select=1),
                'group_id': fields.many2one('mrp_bom_customization.mrp_bom_customization_groups', "Customization Group", required = True),
    }
mrp_bom_customization_values()


class sale_order_line_customization(osv.osv):
    _name = "mrp_bom_customization.sale_order_line_customizations"
    
    #TODO get rid of name
    _columns = {
                'name': fields.related('customization_key_id','name', type="char", string="Name"),
                #'bom_ids': fields.many2many('mrp.bom','mrp_bom_mrp_bom_customizations_rel','mrp_bom_customization_id','bom_id',"BoM's"),
                'sale_order_line_id': fields.many2one('sale.order.line', "Sale order line"),
                'customization_value_id': fields.many2one('mrp_bom_customization.mrp_bom_customization_values', 'Customization Value'),
                'customization_key_id': fields.many2one('mrp_bom_customization.mrp_bom_customization_keys', 'Customization Key'),
    }
sale_order_line_customization()
