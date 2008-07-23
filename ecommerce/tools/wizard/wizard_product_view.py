# -*- encoding: utf-8 -*-
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

