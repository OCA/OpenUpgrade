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
from tools.misc import UpdateableStr
from osv import fields
from osv import osv

FORM = UpdateableStr()

parameter_fields = {
    'segment_id':{'string':'Segment', 'type':'many2one', 'relation':'dm.campaign.proposition.segment', 'required':True},
    'action_id':{'string':'Action', 'type':'many2one', 'relation':'dm.offer.step.transition.trigger', 'required':True , 'domain':[('type','=','as')]},
}

def search_wi(self,cr,uid,data,context):
    pool = pooler.get_pool(cr.dbname)
    wi_obj = pool.get('dm.workitem')
    workitem = wi_obj.search(cr,uid,[('sale_order_id','=',data['id'])])
    if not workitem:
         raise osv.except_osv(
          _('Cannot perfom After-Sale Action'),
          _('This sale order doesnt seem to originate from a Direct Marketing campaign'))

    return wi_obj.browse(cr,uid,workitem[0])
    
def search_criteria(self, cr, uid, data, context):
    wi_browse_id = search_wi(self,cr,uid,data,context)
    FORM.string = """<?xml version="1.0" ?>
    <form string="After-Sale Action">
        <field name="segment_id" colspan="4" domain="[('id', '=', %d)]"/>
        <field name="action_id" colspan="4"/>
    </form>"""%(wi_browse_id.segment_id.id)
    return {}

def _create_dm_event(self,cr,uid,data,context):
    wi_browse_id = search_wi(self,cr,uid,data,context)
    mail_service_step_ids = [step.offer_step_id for step in wi_browse_id.segment_id.proposition_id.camp_id.mail_service_ids]
    mail_service_id = False
    for camp_mail_service in wi_browse_id.segment_id.proposition_id.camp_id.mail_service_ids:
        if wi_browse_id.step_id.id == camp_mail_service.offer_step_id.id:
            mail_service_id = camp_mail_service.mail_service_id.id
        
    vals = {
        'segment_id' : data['form']['segment_id'],
        'step_id' : wi_browse_id.step_id.id,
        'address_id' : wi_browse_id.address_id.id,
        'sale_order_id' : data['id'],
        'trigger_type_id' : data['form']['action_id'],
        'mail_service_id' : mail_service_id
    }
    id = pool.get('dm.event').create(cr,uid,vals,context)
    return {}

class wizard_so_after_sale_action(wizard.interface):
    states = {
        'init':{
            'actions': [search_criteria],
            'result': {'type':'form', 'arch':FORM, 'fields':parameter_fields, 'state':[('end', 'Cancel'),('send', 'Send Document')]},
        },
        'send': {
            'actions': [],
            'result': {'type': 'action', 'action':_create_dm_event, 'state':'end'}
        }
    }
wizard_so_after_sale_action("wizard_so_after_sale_action")
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
