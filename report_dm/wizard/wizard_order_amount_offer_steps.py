# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution	
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>). All Rights Reserved
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
import time
import datetime
import pooler


_order_amount_offer_steps_form = """<?xml version="1.0"?>
<form string="Order quantity per Offer Steps">
   <field name="month"/>
   <field name="year"/>
   <field name="offer_id"/>
</form>"""

_order_amount_offer_steps_fields = {
     'month': dict(string=u'Month', type='selection', required=True, selection=[(x, datetime.date(2000, x, 1).strftime('%B')) for x in range(1, 13)]), 
    'year': dict(string=u'Year', type='integer', required=True),
    'offer_id': {'string': 'Offer', 'type': 'many2one', 'relation': 'dm.offer', 'required': True},
}

def _get_value(self, cr, uid, data, context):
    today=datetime.date.today()
    return dict(month=today.month, year=today.year)
    
    
class wizard_amt_offer_step_report(wizard.interface):
    states = {
        'init': {
            'actions': [_get_value],
            'result': {'type':'form', 'arch':_order_amount_offer_steps_form, 'fields':_order_amount_offer_steps_fields, 'state':[('end','Cancel'),('print','Print Report')]},
        },
        'print': {
            'actions': [],
            'result': {'type':'print', 'report':'dm.order.amount.offer.steps', 'state':'end'},
        },
    }
wizard_amt_offer_step_report('dm.order.amount.offer.steps')

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
