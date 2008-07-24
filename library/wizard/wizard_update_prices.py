# -*- encoding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2005-2006 TINY SPRL. (http://tiny.be) All Rights Reserved.
#                    Fabien Pinckaers <fp@tiny.Be>
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsability of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# garantees and support are strongly adviced to contract a Free Software
# Service Company
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
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

