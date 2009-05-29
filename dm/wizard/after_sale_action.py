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
from osv import fields
from osv import osv

parameter_form = """<?xml version="1.0" ?>
<form string="After-Sale Action">
    <field name="segment_id" colspan="4" context="{'address_id':1}"/>
    <field name="action_id" colspan="4"/>
</form>"""

parameter_fields = {
    'segment_id':{'string':'Segment', 'type':'many2one', 'relation':'dm.campaign.proposition.segment', 'required':True},
    'action_id':{'string':'Action', 'type':'many2one', 'relation':'dm.offer.step.transition.trigger', 'required':True , 'domain':[('type','=','as')]},
}

def _create_event(self, cr, uid, data, context):
    pool = pooler.get_pool(cr.dbname)
    vals = {
        'segment_id' : data['form']['segment_id'],
        'step_id' : pool.get('dm.offer.step').search(cr,uid,[('type_id.code','=','ASEVENT'),('name','=','After-Sale Event (email)')])[0],
        'address_id' : data['id'],
        'trigger_type_id' : data['form']['action_id']
    }
    pool.get('dm.event').create(cr,uid,vals,context)
    return {}

class wizard_after_sale_action(wizard.interface):
    states = {
        'init':{
            'actions': [],
            'result': {'type':'form', 'arch':parameter_form, 'fields':parameter_fields, 'state':[('end', 'Cancel'),('send', 'Send Document')]},
        },
        'send': {
            'actions': [],
            'result': {'type': 'action', 'action':_create_event, 'state':'end'}
        }
    }
wizard_after_sale_action("wizard_after_sale_action")
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: