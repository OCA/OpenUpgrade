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
import time

_event_form = '''<?xml version="1.0"?>
        <form string="Partner Event">
        <separator colspan="4" string="General Description"/>
        <field name="name" select="1"/>
        <field name="partner_type" select="1"/>
        <field name="som" select="1"/>
        <field name="date" select="1"/>
        <field name="canal_id" select="1"/>
        <field name="type" select="1"/>
        <field name="user_id" select="1"/>
        <field name="probability"/>
        <field name="planned_revenue"/>
        <field name="planned_cost"/>
        <separator colspan="4" string="Description"/>
        <field colspan="4" name="description"/>
        <separator colspan="4" string="Document Link"/>
        <field colspan="4" name="document"/>
</form>'''

_event_fields = {
        'user_id': {'domain': [], 'relation': 'res.users', 'string': 'User', 'context': '', 'views': {}, 'type': 'many2one',},
       'name': {'required': True, 'type': 'char', 'string': 'Events', 'size': 64},
       'probability': {'type': 'float', 'string': 'Probability (0.50)'},
       'canal_id': {'domain': [], 'relation': 'res.partner.canal', 'string': 'Channel', 'context': '', 'views': {}, 'type': 'many2one'},
       'type': {'selection': [('sale', 'Sale Opportunity'), ('purchase', 'Purchase Offer'), ('prospect', 'Prospect Contact')], 'type': 'selection', 'string': 'Type of Event'},
       'planned_cost': {'type': 'float', 'string': 'Planned Cost'},
       'description': {'type': 'text', 'string': 'Description'},
       'som': {'domain': [], 'relation': 'res.partner.som', 'string': 'State of Mind', 'context': '', 'views': {}, 'type': 'many2one'},
       'partner_type': {'selection': [('customer', 'Customer'), ('retailer', 'Retailer'), ('prospect', 'Commercial Prospect')], 'type': 'selection', 'string': 'Partner Relation'},
       'planned_revenue': {'type': 'float', 'string': 'Planned Revenue'},
       'date': {'type': 'datetime', 'string': 'Date', 'size': 16, 'default': lambda *a: time.strftime('%Y-%m-%d %H:%M:%S')},
       'document': {'selection': [('product.product', 'Product'), ('crm.case', 'Case'), ('account.invoice', 'Invoice'), ('stock.production.lot', 'Production Lot'), ('project.project', 'Project'), ('project.task', 'Project task'), ('purchase.order', 'Purchase Order'), ('sale.order', 'Sale Order')], 'type': 'reference', 'string': 'Document', 'size': 128}
}
def create_event(self, cr, uid, data, context):
    pool_obj = pooler.get_pool(cr.dbname)
    obj_event = pool_obj.get('res.partner.event')
    for par in data['ids']:
        val = {
           'name' : data['form']['name'],
           'partner_id' : par,
           'user_id' :data['form']['user_id'],
           'probability' :data['form']['probability'],
           'canal_id' :data['form']['canal_id'],
           'type' :data['form']['type'],
           'planned_cost' :data['form']['planned_cost'],
           'description' :data['form']['description'],
           'som' :data['form']['som'],
           'partner_type' :data['form']['partner_type'],
           'planned_revenue' :data['form']['planned_revenue'],
           'date' :data['form']['date'],
           'document' :data['form']['document'],
               }
        id_event_history = obj_event.create(cr,uid,val)
    return {}

class cci_event_history(wizard.interface):
    states = {
        'init': {
            'actions': [],
            'result': {'type': 'form', 'arch':_event_form, 'fields':_event_fields, 'state':[('end','Cancel'),('create','Create Event')]}
        },
        'create': {
            'actions': [create_event],
            'result': {'type': 'state', 'state':'end'}
        }
    }
cci_event_history("cci.partner_event_history")

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

