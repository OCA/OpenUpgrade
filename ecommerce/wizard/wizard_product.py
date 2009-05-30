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

import wizard
import pooler

class ecommerce_productview_wizard(wizard.interface):

    def _action_open_product_view(self, cr, uid, data, context):    
        category_obj = pooler.get_pool(cr.dbname).get('ecommerce.category')
        category_id = category_obj.browse(cr, uid, data['ids'][0]).category_id
        category_name = category_obj.read(cr, uid, data['ids'][0], ['name'])
        
        return  {
            'domain': "[('categ_id', 'child_of',%s)]" % ([category_id.id]),
            'name': category_name['name'],
            'view_type': 'tree',
            'res_model': 'product.product',
            'view_id': False,       
            'type': 'ir.actions.act_window'
        }
                
    states = {
            'init': {
                'actions': [],
                'result': {'type': 'action', 'action': _action_open_product_view, 'state': 'end'}
            }        
    }
ecommerce_productview_wizard('ecommerce_category_product')
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

