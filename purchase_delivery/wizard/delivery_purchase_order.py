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

import time
from datetime import date,timedelta
import wizard
import ir
import pooler

delivery_form = """<?xml version="1.0"?>
<form string="Create deliveries">
    <separator colspan="4" string="Delivery Method" />
    <field name="carrier_id" />
</form>
"""

delivery_fields = {
    'carrier_id' : {'string':'Delivery Method', 'type':'many2one', 'relation': 'delivery.carrier','required':True}
}

def _delivery_default(self, cr, uid, data, context):
    order_obj = pooler.get_pool(cr.dbname).get('purchase.order')
    order = order_obj.browse(cr,uid,data['ids'],)[0]
    if not order.state in ('draft'):
        raise wizard.except_wizard('Order not in draft state !', 'The order state have to be draft to add delivery lines.')
    carrier_id = order.partner_id.property_delivery_carrier.id
    return {'carrier_id': carrier_id}

def _delivery_set(self, cr, uid, data, context):
    order_obj = pooler.get_pool(cr.dbname).get('purchase.order')
    line_obj = pooler.get_pool(cr.dbname).get('purchase.order.line')
    order_objs = order_obj.browse(cr, uid, data['ids'], context)

    for order in order_objs:
#        if not order.dest_address_id:
#            raise wizard.except_wizard('Destination Address is not selected', 'Please select Destination Address for the purchase order')
        grid_id = pooler.get_pool(cr.dbname).get('delivery.carrier').grid_get(cr, uid, [data['form']['carrier_id']],order.partner_address_id.id)
        if not grid_id:
            raise wizard.except_wizard('No grid avaible !', 'No grid matching for this carrier !')
        grid = pooler.get_pool(cr.dbname).get('delivery.grid').browse(cr, uid, [grid_id])[0]

        line_obj.create(cr, uid, {
            'order_id': order.id,
            'name': grid.carrier_id.name,
            'product_qty': 1,
            'product_uom': grid.carrier_id.product_id.uom_id.id,
            'product_id': grid.carrier_id.product_id.id,
            'price_unit': grid.get_price(cr, uid, grid.id, order, time.strftime('%Y-%m-%d'), context={'object':'purchase'}),
            'taxes_id': [(6,0,[ x.id for x in grid.carrier_id.product_id.taxes_id])],
            'date_planned':(date.today() + timedelta(days=1)).strftime('%Y-%m-%d'),

            })

    return {}

class make_delivery(wizard.interface):
    states = {
        'init' : {
            'actions' : [_delivery_default],
            'result' : {'type' : 'form', 'arch' : delivery_form, 'fields' : delivery_fields, 'state' : [('end', 'Cancel'),('delivery', 'Create delivery line') ]}
        },
        'delivery' : {
            'actions' : [_delivery_set],
            'result' : {'type' : 'state', 'state' : 'end'}
        },
    }

make_delivery("delivery.purchase.order")
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

