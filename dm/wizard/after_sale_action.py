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

#def name_search(self, cr, uid, name, args=None, operator='ilike', context=None, limit=80):
#    print "=------------------", name
#    pool = pooler.get_pool(cr.dbname)
#    wi_obj = pool.get('dm.workitem')
#    workitems = wi_obj.search(cr,uid,[('address_id','=',data['id'])])
#    lst = [wi.segment_id.id for wi in wi_obj.browse(cr,uid,workitems)]
#    
#    ids = self.search(cr,uid,['id','in',lst])
#    return self.name_get(cr, uid, ids, context=context)

def _segment(self, cr, uid, data, context):
    print "---------------------", context
    pool = pooler.get_pool(cr.dbname)
    wi_obj = pool.get('dm.workitem')
    workitems = wi_obj.search(cr,uid,[('address_id','=',data['id'])])
    ids = [wi.segment_id.id for wi in wi_obj.browse(cr,uid,workitems)]
    srch_id = pool.get('dm.campaign.proposition.segment').name_search(cr,uid,[('id','in',ids)])
    print "=====================================", srch_id,data['form']
    return data['form']

def temp(self,cr,uid,data,context):
    print "TEMP >>>>>>>>>>>>>>"
    return {}

class wizard_after_sale_action(wizard.interface):
    states = {
        'init':{
            'actions': [],
            'result': {'type':'form', 'arch':parameter_form, 'fields':parameter_fields, 'state':[('end', 'Cancel'),('send', 'Send Document')]},
        },
        'end': {
            'actions': [],
            'result': {'type': 'action', 'action':temp, 'state':'end'}
        }
    }
wizard_after_sale_action("wizard_after_sale_action")
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: