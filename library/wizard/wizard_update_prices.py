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
from osv import osv
import pooler


_upd_form = """<?xml version="1.0"?>
<form string="Update price for products">
    <label string="Update prices for this category ?"/>
</form>
"""
# _upd_fields = {
#   'new_price': {'string':'New Price', 'type':'float', 'required':True},
#   }

_done_form = """<?xml version="1.0"?>
<form string="Update prices">
    <label string="Update Done"/>
</form>
"""

def _action_update_prices(self, cr, uid, data, context):
    pool = pooler.get_pool(cr.dbname)
    prod_obj = pool.get('product.product')
    categories = pool.get('library.price.category').browse(cr,uid,data['ids'])

    for cat in categories:
        prod_ids= []
        for product in cat.product_ids:
            prod_ids.append(product.id)
            
        prod_obj.write(cr,uid,prod_ids,{'list_price':cat.price})
    
    return {}

class wizard_update_prices(wizard.interface):
    states = {
        'init': {'actions': [_action_update_prices],
                 'result' : {'type': 'state','state':'end'}
                 }
    }
wizard_update_prices('library.update.prices')
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

