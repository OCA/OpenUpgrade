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
    'mail_service_id':{'string':'Mail Service', 'type':'many2one', 'relation':'dm.mail_service', 'required':True},
}

def search_segment(self, cr, uid, data, context):
    pool = pooler.get_pool(cr.dbname)
    wi_obj = pool.get('dm.workitem')
    workitems = wi_obj.search(cr,uid,[('address_id','=',data['id'])])
    ids = [wi.segment_id.id for wi in wi_obj.browse(cr,uid,workitems)]
    step_obj = pool.get('dm.offer.step')
    step = step_obj.search(cr,uid,[('type_id.code','=','ASEVENT'),('name','=','After-Sale Event (email)')])[0]
    browse_id = step_obj.browse(cr,uid,step)
    FORM.string = """<?xml version="1.0" ?>
    <form string="After-Sale Action">
        <field name="segment_id" colspan="4" domain="[('id', 'in', [%s])]"/>
        <field name="action_id" colspan="4"/>
        <field name="mail_service_id" colspan="4" domain="[('media_id','=',%d)]"/>
    </form>"""%(','.join([str(x) for x in ids]),browse_id.media_id.id)
    return {}

def _create_event(self,cr,uid,data,context):
    pool = pooler.get_pool(cr.dbname)
    vals = {
        'segment_id' : data['form']['segment_id'],
        'step_id' : pool.get('dm.offer.step').search(cr,uid,[('type_id.code','=','ASEVENT'),('name','=','After-Sale Event (email)')])[0],
        'address_id' : data['id'],
        'trigger_type_id' : data['form']['action_id'],
        'mail_service_id' : data['form']['mail_service_id']
    }
    id = pool.get('dm.event').create(cr,uid,vals,context)
    return {}

class wizard_after_sale_action(wizard.interface):
    states = {
        'init':{
            'actions': [search_segment],
            'result': {'type':'form', 'arch':FORM, 'fields':parameter_fields, 'state':[('end', 'Cancel'),('send', 'Send Document')]},
        },
        'send': {
            'actions': [],
            'result': {'type': 'action', 'action':_create_event, 'state':'end'}
        }
    }
wizard_after_sale_action("wizard_after_sale_action")
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
