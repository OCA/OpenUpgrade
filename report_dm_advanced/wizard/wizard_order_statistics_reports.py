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

from tools.misc import UpdateableDict

Fields = UpdateableDict()

Form = """<?xml version="1.0"?>
<form string="Statistic Reports">
   <field name="month"/>
   <field name="year"/>
   <field name="row_id"/>
   <field name="origin_partner"/>
</form>"""

Fields = {
     'month': dict(string=u'Month', type='selection', required=True, selection=[(x, datetime.date(2000, x, 1).strftime('%B')) for x in range(1, 13)]), 
    'year': dict(string=u'Year', type='integer', required=True),
    'origin_partner':{'string':'Sort by origin partner' , 'type':'boolean'}
}

camp_wiz = ["dm.order.amount.campaign","dm.order.quantity.campaign",  "dm.order.quantity.campaign.offer.step",
            "dm.order.amount.campaign.offer.step"]
offer_wiz = ["dm.order.quantity.offer.steps", "dm.order.amount.offer.steps"]      

def _get_value(self, cr, uid, data, context):
    if self.wiz_name in camp_wiz :
        Fields['row_id']= {'string': 'Campaign', 'type': 'many2one', 'relation': 'dm.campaign', 'required': True}
    elif self.wiz_name in offer_wiz :
        Fields['row_id']= {'string': 'Offer', 'type': 'many2one', 'relation': 'dm.offer', 'required': True}
    today=datetime.date.today()
    return dict(month=today.month, year=today.year)
    
def _report_name(self, cr, uid, data, context):
    self.states['print']['result']['report'] = self.wiz_name
    return {}
    
    
class wizard_amt_campaign_report(wizard.interface):
    states = {
        'init': {
            'actions': [_get_value],
            'result': {'type':'form', 'arch':Form, 'fields':Fields, 'state':[('end','Cancel'),('print','Print Report')]},
        },
        'print': {
            'actions': [_report_name],
            'result': {'type':'print', 'report':'', 'state':'end'},
        },
    }
wizard_amt_campaign_report('dm.order.amount.campaign')
wizard_amt_campaign_report('dm.order.quantity.campaign')
wizard_amt_campaign_report('dm.order.quantity.campaign.offer.step')
wizard_amt_campaign_report('dm.order.amount.campaign.offer.step')
wizard_amt_campaign_report('dm.order.quantity.offer.steps')
wizard_amt_campaign_report('dm.order.amount.offer.steps')



# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
