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

from mx.DateTime import now

import wizard
import netsvc
import ir
import pooler

sale_form = """<?xml version="1.0"?>
<form string="Make an order">
    <field name="name" required="True" />
    <field name="partner_id" required="True" />
</form>"""

sale_fields = {
    'name' : {'string' : 'Order name', 'type': 'char'},
    'partner_id' : {'string':'Suplier', 'relation':'res.partner', 'type':'many2one'},
}

class make_sale(wizard.interface):
    def _makeOrder(self, cr, uid, data, context):
        order = pooler.get_pool(cr.dbname).get('sandwich.order')
        line = pooler.get_pool(cr.dbname).get('sandwich.order.line')
        oid = order.create(cr, uid, {
            'name': data['form']['name'],
            'partner': data['form']['partner_id'],
        })
        cr.execute('update sandwich_order_line set order_id=%s where order_id is null', (oid,))
        value = {
            'domain': "[('id','in',["+str(oid)+"])]",
            'name': 'Create Sandwich Orders',
            'view_type': 'form',
            'view_mode': 'form,tree',
            'res_model': 'sandwich.order',
            'view_id': False,
            'type': 'ir.actions.act_window',
            'res_id': oid
        }
        return value

    states = {
        'init' : {
            'actions' : [],
            'result' : {'type' : 'form', 'arch' : sale_form, 'fields' : sale_fields, 'state' : [('end', 'Cancel'),('order', 'Make an order')]}
        },
        'order' : {
            'actions': [],
            'result': {'type': 'action', 'action': _makeOrder, 'state':'end'},
        }
    }
make_sale('sandwich.order_create')
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

