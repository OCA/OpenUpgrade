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
import netsvc
import pooler
import time
import mx.DateTime
import datetime
import os
from osv import osv
import tools

class wizard_product_ecom_view(wizard.interface):
        def _action_open_product_view(self, cr, uid, data, context):
    
            product_obj = pooler.get_pool(cr.dbname).get('ecommerce.category')
            product_id = product_obj.browse(cr,uid,data['ids'][0]).category_id
         
            print {
                'domain': "[('categ_id','child_of',%s)]" % ([product_id.id]),
                'name': 'Product View',
                'view_type': 'tree',
                'res_model': 'product.product',
                'view_id': False,       
                'type': 'ir.actions.act_window'
            }
            
            return  {
                'domain': "[('categ_id','child_of',%s)]" % ([product_id.id]),
                'name': 'Product View',
                'view_type': 'tree',
                'res_model': 'product.product',
                'view_id': False,       
                'type': 'ir.actions.act_window'
            }
            
        states = {
        'init': {
            'actions': [],
            'result': {'type': 'action', 'action': _action_open_product_view, 'state':'end'}
        },        
    }
    
wizard_product_ecom_view('ecommerce_category_product')
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

