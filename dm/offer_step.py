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
#import campaign

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

class dm_offer_step(osv.osv):
    _name = "dm.offer.step"

    def __history(self, cr, uid, ids, keyword, context={}):
        for id in ids:
            data = {
                'user_id': uid,
                'state' : keyword,
                'step_id': id,
                'date' : time.strftime('%Y-%m-%d')
            }
            obj = self.pool.get('dm.offer.step.history')
            obj.create(cr, uid, data, context)
        return True

    def _offer_step_code(self, cr, uid, ids, name, args, context={}):
        result ={}
        for id in ids:
            code=''
            offer_step = self.browse(cr,uid,[id])[0]
            res_trans = self.pool.get('ir.translation')._get_ids(cr, uid, 'dm.offer.step.type,code', 'model',
                    context.get('lang', False) or 'en_US',[offer_step.type.id])
            type_code = res_trans[offer_step.type.id] or offer_step.type.code
            code = '_'.join([offer_step.offer_id.code,(type_code or '')])
            result[id]=code
        return result

    _columns = {
        'name' : fields.char('Name',size=64, required=True),
        'offer_id' : fields.many2one('dm.offer', 'Offer',required=True, ondelete="cascade"),
        'parent_id' : fields.many2one('dm.offer', 'Parent'),
        'legal_state' : fields.char('Legal State', size=32),
        'code' : fields.function(_offer_step_code,string='Code',type="char",method=True,readonly=True),
        'quotation' : fields.char('Quotation', size=16),
        'media_ids' : fields.many2many('dm.media', 'dm_offer_step_media_rel','step_id','media_id', 'Medias'),
        'type' : fields.many2one('dm.offer.step.type','Type',required=True),
        'origin_id' : fields.many2one('dm.offer.step', 'Origin'),
        'desc' : fields.text('Description'),
        'dtp_note' : fields.text('DTP Notes'),
        'dtp_category_ids' : fields.many2many('dm.offer.category','dm_offer_dtp_category','offer_id','offer_dtp_categ_id', 'DTP Categories') ,# domain="[('domain','=','production')]"),
        'trademark_note' : fields.text('Trademark Notes'),
        'trademark_category_ids' : fields.many2many('dm.offer.category','dm_offer_trademark_category','offer_id','offer_trademark_categ_id','Trademark Categories'),# domain="[('domain','=','purchase')]"),
        'production_note' : fields.text('Production Notes'),
        'planning_note' : fields.text('Planning Notes'),
        'purchase_note' : fields.text('Purchase Notes'),
        'mailing_at_dates' : fields.boolean('Mailing at dates'),
        'floating date' : fields.boolean('Floating date'),
        'interactive' : fields.boolean('Interactive'),
#        'wrkitem_id' : fields.one2many('dm.offer.step.workitem','step_id', 'WorkItems'),
        'notes' : fields.text('Notes'),
        'document_ids' : fields.one2many('dm.offer.document', 'step_id', 'DTP Documents'),
        'flow_start' : fields.boolean('Flow Start'),
        'history_ids' : fields.one2many('dm.offer.step.history', 'step_id', 'History'),
        'item_ids' : fields.one2many('dm.offer.step.item', 'offer_step_id', 'Items'),
        'state' : fields.selection(AVAILABLE_STATES, 'Status', size=16, readonly=True),
        'incoming_transition_ids' : fields.one2many('dm.offer.step.transition','step_to', 'Incoming Transition',readonly=True),
        'outgoing_transition_ids' : fields.one2many('dm.offer.step.transition','step_from', 'Outgoing Transition'),
        'split_mode' : fields.selection([('and','And'),('or','Or'),('xor','Xor')],'Split mode'),
        'doc_number' : fields.integer('Number of documents of the mailing'),
        'manufacturing_constraint_ids': fields.one2many('dm.offer.step.manufacturing_constraint', 'offer_step_id', 'Manufacturing Constraints'),
    }

    _defaults = {
        'state': lambda *a : 'open',
        'split_mode' : lambda *a : 'or',
    }
    
    def onchange_type(self,cr,uid,ids,type,offer_id,context):
        step_type = self.pool.get('dm.offer.step.type').browse(cr,uid,[type])[0]
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
    
    def state_close_set(self, cr, uid, ids, context=None):
        self.__history(cr,uid, ids, 'closed')
        self.write(cr, uid, ids, {'state':'closed'})
        return True

    def state_open_set(self, cr, uid, ids, context=None):
        for step in self.browse(cr,uid,ids,context):
            for doc in step.document_ids:
                if doc.state != 'validate':
                    raise osv.except_osv(
                            _('Could not open this offer step !'),
                            _('You must first validate all documents attached to this offer step.'))
#                    self.pool.get('dm.offer.document').write(cr,uid,[doc.id],{'state':'validate'})
        self.__history(cr,uid,ids, 'open')
        self.write(cr, uid, ids, {'state':'open'})
        return True

    def state_freeze_set(self, cr, uid, ids, context=None):
        self.__history(cr,uid,ids, 'freeze')
        self.write(cr, uid, ids, {'state':'freeze'})
        return True

    def state_draft_set(self, cr, uid, ids, context=None):
        self.__history(cr,uid,ids, 'draft')
        self.write(cr, uid, ids, {'state':'draft'})
        return True

dm_offer_step()

class dm_offer_step_transition(osv.osv):
    _name = "dm.offer.step.transition"
    _rec_name = 'condition'
    _columns = {
        'condition' : fields.selection([('automatic','Automatic'),('purchased','Purchased'),('notpurchased','Not Purchased')], 'Condition',required=True),
        'delay' : fields.integer('Offer Delay' ,required=True),
        'step_from' : fields.many2one('dm.offer.step','From Offer Step',required=True, ondelete="cascade"),
        'step_to' : fields.many2one('dm.offer.step','To Offer Step',required=True, ondelete="cascade"),
        'media_id' : fields.many2one('dm.media','Media',required=True)
    }
    def default_get(self, cr, uid, fields, context={}):
        data = super(dm_offer_step_transition, self).default_get(cr, uid, fields, context)
        if context.has_key('type'):
#            if not context['step_id']:
#                raise osv.except_osv('Error !',"It is necessary to save this offer step before creating a transition")
            data['condition']='automatic'
            data['delay']='0'
            data[context['type']] = context['step_id']
        return data

dm_offer_step_transition()

class dm_offer_step_history(osv.osv):
    _name = "dm.offer.step.history"
    _order = 'date'
    _columns = {
        'step_id' : fields.many2one('dm.offer.step', 'Offer'),
        'user_id' : fields.many2one('res.users', 'User'),
        'state' : fields.selection(AVAILABLE_STATES, 'Status', size=16),
        'date' : fields.date('Date')
    }

    _defaults = {
        'date' : lambda *a: time.strftime('%Y-%m-%d'),
    }

dm_offer_step_history()

class dm_offer_document_category(osv.osv):
    _name = "dm.offer.document.category"
    _rec_name = "name"
    def name_get(self, cr, uid, ids, context={}):
        if not len(ids):
            return []
        reads = self.read(cr, uid, ids, ['name','parent_id'], context)
        res = []
        for record in reads:
            name = record['name']
            if record['parent_id']:
                name = record['parent_id'][1]+' / '+name
            res.append((record['id'], name))
        return res

    def _name_get_fnc(self, cr, uid, ids, prop, unknow_none, unknow_dict):
        res = self.name_get(cr, uid, ids)
        return dict(res)

    _columns = {
        'name' : fields.char('Name', size=64, required=True),
        'complete_name' : fields.function(_name_get_fnc, method=True, type='char', string='Category'),
        'parent_id' : fields.many2one('dm.offer.document.category', 'Parent'),
    }

dm_offer_document_category()

class dm_offer_document(osv.osv):
    _name = "dm.offer.document"
    _rec_name = 'name'
    
    def _has_attchment_fnc(self, cr, uid, ids, name, arg, context={}):
        res={}
        for id in ids :
            attachment_id = self.pool.get('ir.attachment').search(cr,uid,[('res_model','=','dm.offer.document'),('res_id','=',id)])
            if attachment_id :
                res[id]=True
            else :  
                res[id]=False
        return res
    
    _columns = {
        'name' : fields.char('Name', size=64, required=True),
        'code' : fields.char('Code', size=16, required=True),
        'lang_id' : fields.many2one('res.lang', 'Language'),
        'copywriter_id' : fields.many2one('res.partner', 'Copywriter', domain=[('category_id','ilike','Copywriter')], context={'category':'Copywriter'}),
        'category_ids' : fields.many2many('dm.offer.document.category','dm_offer_document_rel', 'doc_id', 'category_id', 'Categories'),
        'step_id': fields.many2one('dm.offer.step', 'Offer Step'),
        'has_attachment' : fields.function(_has_attchment_fnc, method=True, type='char', string='Has Attachment'),
        'customer_field_ids': fields.many2many('ir.model.fields','dm_doc_customer_field_rel',
              'document_id','customer_field_id','Customer Fields',
               domain=[('model_id','like','dm.customer')],context={'model':'dm.customer'}),
#               domain=['&',('model_id','like','dm.customer'),'!',('model_id','like','dm.customer.order'),'!',('model_id','like','dm.customers_list')],context={'model':'dm.customer'}),
        'customer_order_field_ids': fields.many2many('ir.model.fields','dm_doc_customer_order_field_rel',
              'document_id','customer_order_field_id','Customer Order Fields',
               domain=[('model_id','like','dm.customer.order')],context={'model':'dm.customer.order'}),
        'state' : fields.selection([('draft','Draft'),('validate','Validated')], 'Status', readonly=True),
    }
    _defaults = {
        'state': lambda *a: 'draft',
    }
    def fields_view_get(self, cr, user, view_id=None, view_type='form', context=None, toolbar=False):
        result=super(dm_offer_document,self).fields_view_get(cr, user, view_id, view_type, context, toolbar)
        if result['type']=='form' and 'toolbar' in result:
            result['toolbar']['print']=[]
        return result
    def state_validate_set(self, cr, uid, ids, context={}):
        self.write(cr, uid, ids, {'state':'validate'})
        return True
  
dm_offer_document()


class dm_offer_step_item(osv.osv):
    _name = "dm.offer.step.item"

    def _step_type(self, cr, uid, ids, name, args, context={}):
        result={}
        for id in ids:
            result[id] = self.browse(cr, uid, id).offer_step_id.type.code
        return result

    _rec_name = 'product_id'
    _columns = {
        'product_id' : fields.many2one('product.product', 'Product', required=True, context={'flag':True}),
        'offer_step_id': fields.many2one('dm.offer.step', 'Offer Step'),
        'offer_step_type': fields.function(_step_type,string='Offer Step Type',type="char",method=True,readonly=True), 
        'item_type': fields.selection(AVAILABLE_ITEM_TYPES, 'Item Type', size=64),
        'price' : fields.float('Price',digits=(16,2)),
        'forwarding_charges' : fields.float('Forwarding Charges',digits=(16,2)),
        'notes' : fields.text('Notes'),
        'purchase_constraints' : fields.text('Purchase Constraints'),
    }
dm_offer_step_item()


class dm_offer_step_manufacturing_constraint(osv.osv):
    _name = "dm.offer.step.manufacturing_constraint"
    _columns = {
        'name': fields.char('Description', size=64, required=True),
        'country_ids': fields.many2many('res.country','dm_manuf_constraint_country_rel','manuf_constraint_id','country_id','Country'),
        'constraint': fields.text('Manufacturing Description'),
        'offer_step_id': fields.many2one('dm.offer.step', 'Offer Step'),
    }
dm_offer_step_manufacturing_constraint()


class product_product(osv.osv):
    _name = "product.product"
    _inherit = "product.product"

    def fields_view_get(self, cr, user, view_id=None, view_type='form', context=None, toolbar=False):
        result=super(product_product,self).fields_view_get(cr, user, view_id, view_type, context, toolbar)
        if 'flag' in context:
            if result['type']=='form':
                for k,v in result['fields'].items():
                    if not (k=='name' or k=='default_code' or k=='categ_id' or k=='list_price' or k=='standard_price' or k=='seller_ids' \
                        or k=='description' or k=='description_sale'  or k=='description_purchase'):
                        del result['fields'][k]

                result['arch']= """<?xml version="1.0" encoding="utf-8"?>\n<form string="Product">\n<notebook>\n<page string="General">\n<field name="name" select="1"/>\n<field name="default_code" select="1"/>\n<field name="categ_id" select="1"/>\n<field name="list_price"/>\n<field name="standard_price"/>\n<field colspan="4" name="seller_ids" nolabel="1" widget="one2many_list"/>\n</page>\n
                    <page string="Descriptions">\n<separator string="Description" colspan="4"/>\n<field colspan="4" name="description" nolabel="1"/>\n<separator string="Sale Description" colspan="4"/>\n
                    <field colspan="4" name="description_sale" nolabel="1"/>\n<separator string="Purchase Description" colspan="4"/>\n<field colspan="4" name="description_purchase" nolabel="1"/>\n</page>\n</notebook>\n</form>"""
        return result

product_product()


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

