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
import netsvc
import datetime

from osv import fields
from osv import osv
from tools import translate 

AVAILABLE_STATES = [
    ('draft','Draft'),
    ('open','Open'),
    ('freeze', 'Freeze'),
    ('closed', 'Close')
]

AVAILABLE_ITEM_TYPES = [
    ('main','Main Item'),
    ('standart','Standart Item'),
]


class dm_offer_step_type(osv.osv):
    _name="dm.offer.step.type"
    _rec_name = 'name'

    _columns = {
        'name' : fields.char('Name', size=64, translate=True, required=True),
        'code' : fields.char('Code', size=8, translate=True, required=True),
        'flow_start' : fields.boolean('Flow Start'),
        'flow_stop' : fields.boolean('Flow Stop'),
        'description' : fields.text('Description', translate=True),
        }

    _sql_constraints = [
        ('code_uniq', 'UNIQUE(code)', 'The code must be unique!'),
    ]

dm_offer_step_type()

class dm_offer_step_action(osv.osv):
    _name = 'dm.offer.step.action'
    _inherits = {'ir.actions.server':'server_action_id'}
    _columns = {
        'server_action_id' : fields.many2one('ir.actions.server','Server Action'),
        'media_id' : fields.many2one('dm.media','Media',required=True)
    }
dm_offer_step_action()

class dm_offer_step(osv.osv):
    _name = "dm.offer.step"

#    def _offer_step_code(self, cr, uid, ids, name, args, context={}):
#        result ={}
#        for id in ids:
#            offer_step = self.browse(cr,uid,[id])[0]
#            step_code = self.pool.get('ir.translation')._get_ids(cr, uid, 'dm.offer.step.type,code', 'model', context.get('lang', False) or 'en_US',[offer_step.type_id.id])
#            type_code = (step_code[offer_step.type_id.id] or offer_step.type_id.code) + str(offer_step.seq)
#            offer_code = self.pool.get('ir.translation')._get_ids(cr, uid, 'dm.offer,code', 'model', context.get('lang', False) or 'en_US',[offer_step.offer_id.id])
#            code = (offer_code[offer_step.offer_id.id] or offer_step.offer_id.code) + '_' + type_code
#            result[id] = str(code)
#        return result

    _columns = {
        'seq' : fields.integer('Step Type Sequence'),
        'name' : fields.char('Name',size=64, required=True, states={'closed':[('readonly',True)]}),
        'offer_id' : fields.many2one('dm.offer', 'Offer',required=True, ondelete="cascade", states={'closed':[('readonly',True)]}),
        'parent_id' : fields.many2one('dm.offer', 'Parent'),
        'legal_state' : fields.char('Legal State', size=32, states={'closed':[('readonly',True)]}),
#        'code' : fields.function(_offer_step_code,string='Code',type="char",method=True,size=64),
        'code' : fields.char('Code',size=64,required=True,translate=True),
        'quotation' : fields.char('Quotation', size=16, states={'closed':[('readonly',True)]}),
        'media_id' : fields.many2one('dm.media', 'Media', ondelete="cascade",required=True, states={'closed':[('readonly',True)]}),
        'type_id' : fields.many2one('dm.offer.step.type','Type',required=True, states={'closed':[('readonly',True)]}),
        'origin_id' : fields.many2one('dm.offer.step', 'Origin'),
        'desc' : fields.text('Description', states={'closed':[('readonly',True)]}),
        'dtp_note' : fields.text('DTP Notes', states={'closed':[('readonly',True)]}),
        'dtp_category_ids' : fields.many2many('dm.offer.category','dm_offer_dtp_category','offer_id','offer_dtp_categ_id', 'DTP Categories'),
        'trademark_note' : fields.text('Trademark Notes', states={'closed':[('readonly',True)]}),
        'trademark_category_ids' : fields.many2many('dm.offer.category','dm_offer_trademark_category','offer_id','offer_trademark_categ_id','Trademark Categories'),
        'production_note' : fields.text('Production Notes', states={'closed':[('readonly',True)]}),
        'planning_note' : fields.text('Planning Notes', states={'closed':[('readonly',True)]}),
        'purchase_note' : fields.text('Purchase Notes', states={'closed':[('readonly',True)]}),
        'mailing_at_dates' : fields.boolean('Mailing at dates', states={'closed':[('readonly',True)]}),
        'floating_date' : fields.boolean('Floating date', states={'closed':[('readonly',True)]}),
        'interactive' : fields.boolean('Interactive', states={'closed':[('readonly',True)]}),
        'notes' : fields.text('Notes'),
        'document_ids' : fields.one2many('dm.offer.document', 'step_id', 'DTP Documents'),
        'flow_start' : fields.boolean('Flow Start'),
        'item_ids' : fields.many2many('product.product','dm_offer_step_product_rel','product_id','offer_step_id','Items', states={'closed':[('readonly',True)]}),
        'state' : fields.selection(AVAILABLE_STATES, 'Status', size=16, readonly=True),
        'incoming_transition_ids' : fields.one2many('dm.offer.step.transition','step_to_id', 'Incoming Transition',readonly=True),
        'outgoing_transition_ids' : fields.one2many('dm.offer.step.transition','step_from_id', 'Outgoing Transition', states={'closed':[('readonly',True)]}),
        'split_mode' : fields.selection([('and','And'),('or','Or'),('xor','Xor')],'Split mode'),
        'doc_number' : fields.integer('Number of documents of the mailing', states={'closed':[('readonly',True)]}),
        'manufacturing_constraint_ids' : fields.many2many('product.product','dm_offer_step_manufacturing_product_rel','product_id','offer_step_id','Mailing Manufacturing Products',domain=[('categ_id', 'ilike', 'Mailing Manufacturing')], states={'closed':[('readonly',True)]}),
        'action_id' : fields.many2one('dm.offer.step.action', string="Action", required=True, domain="[('dm_action','=',True)]"),
        'forecasted_yield' : fields.float('Forecasted Yield'),
    }

    _defaults = {
        'state': lambda *a : 'draft',
        'split_mode' : lambda *a : 'or',
    }

    def onchange_code(self,cr,uid,ids,type_id,context):
        step_type = self.pool.get('dm.offer.step.type').browse(cr,uid,[type_id])[0]
        res_code = self.pool.get('ir.translation')._get_ids(cr, uid, 'dm.offer.step.type,code', 'model', context.get('lang', False) or 'en_US',[step_type.id])
        type_code = res_code[step_type.id] or step_type.code
        value = {
                 'code' : type_code
                }
        return {'value':value}

    def onchange_type(self,cr,uid,ids,type_id,offer_id,context):
        step_type = self.pool.get('dm.offer.step.type').browse(cr,uid,[type_id])[0]
        value = {
                    'flow_start':step_type['flow_start'],
                }
        if offer_id :
            offer = self.pool.get('dm.offer').browse(cr,uid,[offer_id])[0]
            if offer.type == 'model':
                res_trans = self.pool.get('ir.translation')._get_ids(cr, uid, 'dm.offer.step.type,name', 'model', context.get('lang', False) or 'en_US',[step_type.id])
                type_code = res_trans[step_type.id] or step_type.name
                value['name'] = step_type.name
            else :
                res_code = self.pool.get('ir.translation')._get_ids(cr, uid, 'dm.offer.step.type,code', 'model', context.get('lang', False) or 'en_US',[step_type.id])
                type_code = res_code[step_type.id] or step_type.code
#                res_offer = self.pool.get('ir.translation')._get_ids(cr, uid, 'dm.offer,name', 'model', context.get('lang', False) or 'en_US',[offer.id])
#                offer_name = res_offer[offer.id] or offer.name
                value['name'] = "%s for %s"% (type_code,offer.name) 
        return {'value':value}

    def create(self,cr,uid,vals,context={}):
        type_seq = self.search(cr,uid,[('type_id','=',vals['type_id']),('offer_id','=',vals['offer_id'])])
        vals['seq'] = len(type_seq) and len(type_seq)+1 or 1
        return super(dm_offer_step,self).create(cr,uid,vals,context)

    def write(self,cr,uid,ids,vals,context={}):
        if 'type_id' in vals :
            step  = self.browse(cr,uid,ids)[0]
            if vals['type_id'] != step.type_id.id :
                type_seq = self.search(cr,uid,[('type_id','=',vals['type_id']),('offer_id','=',step.offer_id.id)])
                vals['seq'] = len(type_seq) and len(type_seq)+1 or 1
        return super(dm_offer_step,self).write(cr,uid,ids,vals,context)


    def state_close_set(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state':'closed'})
        return True

    def state_open_set(self, cr, uid, ids, context=None):
        wf_service = netsvc.LocalService("workflow")
        for step in self.browse(cr,uid,ids,context):
            for doc in step.document_ids:
                if doc.state != 'validate':
                    raise osv.except_osv(
                            _('Could not open this offer step !'),
                            _('You must first validate all documents attached to this offer step.'))
            wf_service.trg_validate(uid, 'dm.offer.step', step.id, 'open', cr)
        self.write(cr, uid, ids, {'state':'open'})
        return True

    def state_freeze_set(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state':'freeze'})
        return True

    def state_draft_set(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state':'draft'})
        return True
    
    def search(self, cr, uid, args, offset=0, limit=None, order=None, context=None, count=False):
        if context and 'dm_camp_id' in context:
            if not context['dm_camp_id']:
                return []
            res  = self.pool.get('dm.campaign').browse(cr, uid,context['dm_camp_id'])
            step_ids = map(lambda x : x.id, res.offer_id.step_ids)
            return step_ids
        return super(dm_offer_step, self).search(cr, uid, args, offset, limit, order, context, count)


dm_offer_step()

class dm_offer_step_transition_trigger(osv.osv):
    _name = "dm.offer.step.transition.trigger"
    _columns = {
        'name' : fields.char('Trigger Name', size=64, required=True, translate=True),
        'code' : fields.char('Code' , size=64, required=True, translate=True),
        'gen_next_wi' : fields.boolean('Auto Generate Next Workitems'),
        'in_act_cond' : fields.text('Action Condition', required=True),
#        'out_act_cond' : fields.text('Outgoing Action Condition', required=True),
    }
    _defaults = {
        'gen_next_wi': lambda *a: 'False',
        'in_act_cond': lambda *a: 'result = False',
#        'out_act_cond': lambda *a: 'result = False',
    }
dm_offer_step_transition_trigger()

class dm_offer_step_transition(osv.osv):
    _name = "dm.offer.step.transition"
    _rec_name = 'condition_id'
    _columns = {
        'condition_id' : fields.many2one('dm.offer.step.transition.trigger','Trigger Condition',required=True,ondelete="cascade"),
        'delay' : fields.integer('Offer Delay' ,required=True),
        'delay_type' : fields.selection([('minute', 'Minutes'),('hour','Hours'),('day','Days'),('week','Weeks'),('month','Months')], 'Delay type', required=True),
        'step_from_id' : fields.many2one('dm.offer.step','From Offer Step',required=True, ondelete="cascade"),
        'step_to_id' : fields.many2one('dm.offer.step','To Offer Step',required=True, ondelete="cascade"),
    }
    _defaults = {
        'delay_type': lambda *a: 'day',
    }
    def default_get(self, cr, uid, fields, context={}):
        data = super(dm_offer_step_transition, self).default_get(cr, uid, fields, context)
        if context.has_key('type_id'):
            data['delay']='0'
            data[context['type_id']] = context['step_id']
        return data

dm_offer_step_transition()

class product_product(osv.osv):
    _name = "product.product"
    _inherit = "product.product"
    _columns = {
        'country_ids' : fields.many2many('res.country', 'product_country_rel', 'product_id', 'country_id', 'Allowed Countries'),
        'state_ids' : fields.many2many('res.country.state','product_state_rel', 'product_id', 'state_id', 'Allowed States'),
        'language_id' : fields.many2one('res.lang', 'Language'),
    }

    def _default_all_country(self, cr, uid, context={}):
        id_country = self.pool.get('res.country').search(cr,uid,[])
        return id_country

    def _default_all_state(self, cr, uid, context={}):
        id_state = self.pool.get('res.country.state').search(cr,uid,[])
        return id_state

    _defaults = {
        'country_ids': _default_all_country,
        'state_ids': _default_all_state,
    }

    def search(self, cr, uid, args, offset=0, limit=None, order=None, context={}, count=False):
            result = super(product_product,self).search(cr,uid,args,offset,limit,order,context,count)
            if 'offer_id' in context and context['offer_id']:
                result = []
                offer_browse_id = self.pool.get('dm.offer').browse(cr,uid,context['offer_id'])
                for step in offer_browse_id.step_ids:
                    for item in step.item_ids:
                        result.append(item.id)
            return result
product_product()

class actions_server(osv.osv):
    _name = 'ir.actions.server'
    _inherit = 'ir.actions.server'
    _columns = {
        'dm_action' : fields.boolean('Action')
    }
actions_server()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

