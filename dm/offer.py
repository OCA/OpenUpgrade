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
#import offer_step

from osv import fields
from osv import osv

AVAILABLE_STATES = [
    ('draft','Draft'),
    ('open','Open'),
    ('freeze', 'Freeze'),
    ('closed', 'Close'),
]

AVAILABLE_TYPE = [
    ('model','Model'),
    ('new','New'),
    ('standart','Standart'),
    ('rewrite','Rewrite'),
    ('preoffer','Offer Idea')
]


class dm_media(osv.osv):
    _name = "dm.media"
    
    def search(self, cr, uid, args, offset=0, limit=None, order=None,
            context=None, count=False):
        if 'step_media_ids' in context and context['step_media_ids']:
            if context['step_media_ids'][0][2]:
                brse_rec = context['step_media_ids'][0][2]
            else:
                raise osv.except_osv('Error !',"It is necessary to select media in offer step.")
        else:
            brse_rec = super(dm_media, self).search(cr, uid, [])
        return brse_rec      
    
    _columns = {
        'name' : fields.char('Media', size=64, translate=True, required=True),
    }
dm_media()

class dm_offer_category(osv.osv):
    _name = "dm.offer.category"
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

    def _check_recursion(self, cr, uid, ids):
        level = 100
        while len(ids):
            cr.execute('select distinct parent_id from dm_offer_category where id in ('+','.join(map(str,ids))+')')
            ids = filter(None, map(lambda x:x[0], cr.fetchall()))
            if not level:
                return False
            level -= 1
        return True     

    _columns = {
        'complete_name' : fields.function(_name_get_fnc, method=True, type='char', string='Category'),
        'parent_id' : fields.many2one('dm.offer.category', 'Parent'),
        'name' : fields.char('Name', size=64, required=True),
        'child_ids': fields.one2many('dm.offer.category', 'parent_id', 'Childs Category'),
    }

    _constraints = [
        (_check_recursion, 'Error ! You can not create recursive categories.', ['parent_id'])
    ]

dm_offer_category()

class dm_offer_production_cost(osv.osv):
    _name = "dm.offer.production.cost"
    _columns = {
        'name' : fields.char('Name', size=32, required=True)
    }

dm_offer_production_cost()
"""
class dm_customers_list(osv.osv):
    _name = "dm.customers_list"
    _columns = {
        'name' : fields.char('Name', size=64, required=True),
        'code' : fields.char('Code', size=16, required=True),
        'broker_id' : fields.many2one('res.partner', 'Broker', domain=[('category_id','ilike','Broker')], context={'category':'Broker'}),
        'delivery_date' : fields.date('Delivery Date'),
        'segment_ids' : fields.one2many('dm.campaign.proposition.segment', 'list_id', 'Segments', readonly=True),
    }
dm_customers_list()

class dm_order(osv.osv):
    _name = "dm.order"
    _columns = {
        'raw_datas' : fields.char('Raw Datas', size=128),
        'customer_code' : fields.char('Customer Code',size=64),
        'title' : fields.char('Title',size=32),
        'customer_firstname' : fields.char('First Name', size=64),
        'customer_lastname' : fields.char('Last Name', size=64),
        'customer_add1' : fields.char('Address1', size=64),
        'customer_add2' : fields.char('Address2', size=64),
        'customer_add3' : fields.char('Address3', size=64),
        'customer_add4' : fields.char('Address4', size=64),
        'country' : fields.char('Country', size=16),
        'zip' : fields.char('Zip Code', size=12),
        'zip_summary' : fields.char('Zip Summary', size=64),
        'distribution_office' : fields.char('Distribution Office', size=64),
        'segment_code' : fields.char('Segment Code', size=64),
        'offer_step_code' : fields.char('Offer Step Code', size=64),
        'state' : fields.selection([('draft','Draft'),('done','Done')], 'Status', readonly=True),
    }
    _defaults = {
        'state': lambda *a: 'draft',
    }

    def set_confirm(self, cr, uid, ids, *args):

        return True

    def onchange_rawdatas(self,cr,uid,ids,raw_datas):
        if not raw_datas:
            return {}
        raw_datas = "2;00573G;162220;MR;Shah;Harshit;W Sussex;;25 Oxford Road;;GBR;BN;BN11 1XQ;WORTHING.LU.SX"
        value = raw_datas.split(';')
        key = ['datamatrix_type','segment_code','customer_code','title','customer_lastname','customer_firstname','customer_add1','customer_add2','customer_add3','customer_add4','country','zip_summary','zip','distribution_office']
        value = dict(zip(key,value))
        return {'value':value}

dm_order()

class dm_customer(osv.osv):
    _name = "dm.customer"
    _columns = {
        'code' : fields.char('Code',size=64),
        'language_id' : fields.many2one('res.lang','Main Language'),
        'language_ids' : fields.many2many('res.lang','dm_customer_langs','lang_id','customer_id','Other Languages'),
        'prospect_media_ids' : fields.many2many('dm.media','dm_customer_prospect_media','prospect_media_id','customer_id','Prospect for Media'),
        'client_media_ids' : fields.many2many('dm.media','dm_customer_client_media','client_media_id','customer_id','Client for Media'),
        'title' : fields.char('Title',size=32),
        'firstname' : fields.char('First Name', size=64),
        'lastname' : fields.char('Last Name', size=64),
        'add1' : fields.char('Address1', size=64),
        'add2' : fields.char('Address2', size=64),
        'add3' : fields.char('Address3', size=64),
        'add4' : fields.char('Address4', size=64),
        'country_id' : fields.many2one('res.country','Country'),
        'zip' : fields.char('Zip Code', size=16),
        'zip_summary' : fields.char('Zip Summary', size=64),
        'distribution_office' : fields.char('Distribution Office', size=64),
    }
dm_customer()

class dm_customer_order(osv.osv):
    _name = "dm.customer.order"
    _columns ={
        'customer_id' : fields.many2one('dm.customer', 'Customer', ondelete='cascade'),
        'segment_id' : fields.many2one('dm.campaign.proposition.segment','Segment'),
        'offer_step_id' : fields.many2one('dm.offer.step','Offer Step'),
        'note' : fields.text('Notes'),
        'state' : fields.selection([('draft','Draft'),('done','Done')], 'Status', readonly=True),
    }
    _defaults = {
        'state': lambda *a: 'draft',
    }
"""

"""
    def set_confirm(self, cr, uid, ids, *args):
        res = self.browse(cr,uid,ids)[0]
#        if res.customer_id:
#            customer = self.pool.get('dm.customer').browse(cr,uid,[res.customer_id])[0]
#            vals = {}
#            if res.name != customer.name:
#                 vals['name'] = customer.name
#            if res.customer_number != customer.customer_number:
#                 vals['customer_number'] = customer.customer_number
        customer_id = res.customer_id.id

        # Create Customer

        if not res.customer_id:
              vals={}
              vals['customer_code']=res.customer_code
              vals['name'] = ( res.customer_firstname or '') + ' ' + (res.customer_lastname or '')
              address={'city':res.customer_add3,
                       'name': vals['name'], 
                       'zip': res.zip, 
                       'title': res.title, 
                       'street2': res.customer_add2, 
                       'street': res.customer_add1,
                    }
#              state_id = self.pool.get("res.country.state")
#              country_id = self.pool.get("res.country")
              vals['address'] = [[0, 0,address]]
              print "DEBUG - customer vals : ",vals
              customer_id = self.pool.get('dm.customer').create(cr,uid,vals)
              print "DEBUG - created new customer : ",customer_id
        # Workitem

        segment = self.pool.get('dm.campaign.proposition.segment')
        segment_id = segment.search(cr,uid,[('action_code','=',res.action_code)])
        if not segment_id :
            raise osv.except_osv('Warning', 'No matching code found in campaign segment')
        workitem = self.pool.get('dm.offer.step.workitem')
        workitem_id = workitem.search(cr,uid,[('customer_id','=',res.customer_id.id),('segment_id','=',segment_id[0])])
        vals={}

        segment_obj = segment.browse(cr,uid,segment_id)[0]
        offer_id = segment_obj.proposition_id.camp_id.offer_id.id
        offer_step = self.pool.get('dm.offer.step')
        step_id = offer_step.search(cr,uid,[('offer_id','=',offer_id),('type','=',res.offer_step)])

        vals['step_id'] =step_id[0]

        step = offer_step.browse(cr,uid,step_id)[0]

        # change the loop
        amount = 0
        for p in step.product_ids:
            amount+=p.price
        vals['purchase_amount']= amount

        # change workitem
        if workitem_id : 

            print "DEBUG - updating workitem for customer"
            workitem.write(cr,uid,workitem_id,vals)
        # create new workitem
        else:
            vals['customer_id']=customer_id
            if segment_id :
                vals['segment_id']=segment_id[0]
            print "DEBUG - Creating new workitem for customer"
            workitem.create(cr,uid,vals)

        self.write(cr,uid,ids,{'state':'done','customer_id':customer_id})
        return True
"""

#dm_customer_order()

class dm_offer(osv.osv):
    _name = "dm.offer"
    _rec_name = 'name'
    
    #    def __history(self, cr, uid, ids, keyword, context={}):
#    def read(self,cr, uid, ids, fields=None, context=None, load='_classic_read'):
#        print "iiiiiiiiiiiiiiiiiiiiiii", ids
#        for id in ids:
#            camp_id = self.pool.get('dm.campaign').search(cr, uid, [('offer_id','=',id)])
#            print "camp_id:::::::", camp_id
#            for i in camp_id:
#                browse_id = self.pool.get('dm.campaign').browse(cr, uid, [i])[0]
#                print "browse_id:::::::", browse_id
#                data = {
#                    'date' : browse_id.date_start,
#                    'responsible': browse_id.responsible_id.name,
#    #                'state' : keyword,
#                    'offer_id': id,
#                    'campaign': browse_id.name,
#                    'code': browse_id.code1,
#                }
#                print "DATA:::::::", data
#                obj = self.pool.get('dm.offer.history')
#                obj.create(cr, uid, data, context)
#        return super(dm_offer, self).read(cr, uid, ids, fields=fields, context=context, load=load)

    def dtp_last_modification_date(self, cr, uid, ids, field_name, arg, context={}):
        result={}
        for id in ids:
            sql = "select write_date,create_date from dm_offer where id = %d"%id
            cr.execute(sql)
            res = cr.fetchone()
            if res[0]:
                result[id]=res[0].split(' ')[0]
            else :
                result[id]=res[1].split(' ')[0]
        return result

    def _check_preoffer(self, cr, uid, ids):
        offer = self.browse(cr,uid,ids)[0]
        if offer.preoffer_original_id:
            preoffer_id = self.search(cr,uid,[('preoffer_original_id','=',offer.preoffer_original_id.id)])
            if len(preoffer_id) > 1 :
                return False
        return True

    _columns = {
        'name' : fields.char('Name', size=64, required=True),
        'code' : fields.char('Code', size=16, required=True),
        'lang_orig' : fields.many2one('res.lang', 'Original Language'),
        'copywriter_id' : fields.many2one('res.partner', 'Copywriter',domain=[('category_id','ilike','Copywriter')], context={'category':'Copywriter'}),
        'step_ids' : fields.one2many('dm.offer.step','offer_id','Offer Steps'),
        'offer_responsible_id' : fields.many2one('res.users','Responsible',ondelete="cascade"),
        'recommended_trademark' : fields.many2one('dm.trademark','Recommended Trademark'),
        'offer_origin_id' : fields.many2one('dm.offer', 'Original Offer',domain=[('type','in',['new','standart','rewrite'])]),
        'preoffer_original_id' : fields.many2one('dm.offer', 'Original Offer Idea',domain=[('type','=','preoffer')] ),
        'active' : fields.boolean('Active'),
        'quotation' : fields.char('Quotation', size=16),
        'legal_state' : fields.selection([('validated','Validated'), ('notvalidated','Not Validated'), ('inprogress','In Progress'), ('refused','Refused')],'Legal State'),
        'category_ids' : fields.many2many('dm.offer.category','dm_offer_category_rel', 'offer_id', 'offer_category_id', 'Categories'),
        'notes' : fields.text('General Notes'),
        'state': fields.selection(AVAILABLE_STATES, 'Status', size=16, readonly=True),
        'type' : fields.selection(AVAILABLE_TYPE, 'Type', size=16),
        'preoffer_offer_id' : fields.many2one('dm.offer', 'Offer',domain=[('type','in',['new','standart','rewrite'])]),
        'preoffer_type' : fields.selection([('rewrite','Rewrite'),('new','New')], 'Type', size=16),
        'production_category_ids' : fields.many2many('dm.offer.category','dm_offer_production_category','offer_id','offer_production_categ_id', 'Production Categories' , domain="[('domain','=','production')]"),
        'production_cost' : fields.many2one('dm.offer.production.cost', 'Production Cost'),
        'purchase_note' : fields.text('Purchase Notes'),
        'purchase_category_ids' : fields.many2many('dm.offer.category','dm_offer_purchase_category','offer_id','offer_purchase_categ_id', 'Purchase Categories', domain="[('domain','=','purchase')]"),
        'history_ids' : fields.one2many('dm.offer.history', 'offer_id', 'History', ondelete="cascade", readonly=True),
        'translation_ids' : fields.one2many('dm.offer.translation', 'offer_id', 'Translations', ondelete="cascade", readonly=True),
        'order_date' : fields.date('Order Date'),
        'last_modification_date' : fields.function(dtp_last_modification_date, method=True,type="char", string='Last Modification Date',readonly=True),
        'planned_delivery_date' : fields.date('Planned Delivery Date'),
        'delivery_date' : fields.date('Delivery Date'),
        'fixed_date' : fields.date('Fixed Date'),
        'forbidden_country_ids' : fields.many2many('res.country','dm_offer_forbidden_country', 'offer_id', 'country_id', 'Forbidden Countries'),
        'forbidden_state_ids' : fields.many2many('res.country.state','dm_offer_forbidden_state', 'offer_id', 'state_id', 'Forbidden States'),
        'keywords' :fields.text('Keywords'),
        'version' : fields.float('Version'),
        'child_ids': fields.one2many('dm.offer', 'offer_origin_id', 'Childs Category'),
    }

    _defaults = {
        'active': lambda *a: 1,
        'state': lambda *a: 'draft',
        'type': lambda *a: 'new',
        'preoffer_type': lambda *a: 'new',
        'legal_state': lambda *a: 'validated',
        'offer_responsible_id' : lambda obj, cr, uid, context: uid,
    }

    _constraints = [
        (_check_preoffer, 'Error ! this offer idea is already assigned to an offer',['preoffer_original_id'])
    ]

#    def change_code(self,cr,uid,ids,type,copywriter_id) :
#        if type=='model' and ids:
#            return {'value':{'code':'Model%%0%sd' % 3 % ids[0]}}
#        if copywriter_id and ids:
#            copywriter = self.pool.get('res.partner').browse(cr,uid,[copywriter_id])[0]
#            code = ( copywriter.ref or '')+'%%0%sd' % 3 % ids[0]
#            return {'value':{'code':code}}
#        return {'value':{'code':''}}

    def state_close_set(self, cr, uid, ids, *args):
#        self.__history(cr,uid, ids, 'closed')
        self.write(cr, uid, ids, {'state':'closed'})
        return True  

    def state_open_set(self, cr, uid, ids, *args):
        for step in self.browse(cr,uid,ids):
            for step_id in step.step_ids:
                if step_id.state != 'open':
                    raise osv.except_osv(
                            _('Could not open this offer !'),
                            _('You must first open all offer steps related to this offer.'))
#        self.__history(cr,uid, ids, 'open')
        self.write(cr, uid, ids, {'state':'open'})
        return True 
    
    def state_freeze_set(self, cr, uid, ids, *args):
#        self.__history(cr,uid,ids, 'freeze')
        self.write(cr, uid, ids, {'state':'freeze'})
        return True
    
    def state_draft_set(self, cr, uid, ids, *args):
#        self.__history(cr,uid,ids, 'draft')
        self.write(cr, uid, ids, {'state':'draft'})
        wf_service = netsvc.LocalService("workflow")
        for off_id in ids:
            wf_service.trg_create(uid, 'dm.offer', off_id, cr)
        return True  
    
    def go_to_offer(self,cr, uid, ids, *args):
        self.copy(cr,uid,ids[0],{'type':'standart'})
#        self.__history(cr,uid,ids, 'open')
        #self.write(cr, uid, ids, {'state':'open'})
        return True
    
    def fields_view_get(self, cr, user, view_id=None, view_type='form', context=None, toolbar=False):
        if context.has_key('offer_type') and context['offer_type'] :
            new_view_id = self.pool.get('ir.ui.view').search(cr,user,[('name','=','dm.preoffer.form')])
            result = super(dm_offer,self).fields_view_get(cr, user, new_view_id[0], view_type, context, toolbar)
        else : 
            result = super(dm_offer,self).fields_view_get(cr, user, view_id, view_type, context, toolbar)
            if context.has_key('type'):
                if context['type'] == 'model' :
                    if result.has_key('toolbar'):
                        if result['toolbar'].has_key('print'):
                            new_print = filter(lambda x : x['report_name'] not in ['offer.report','preoffer.report'],result['toolbar']['print'])
                            result['toolbar']['print'] =new_print
                if context['type'] == 'preoffer' :
                    if result.has_key('toolbar'):
                        if result['toolbar'].has_key('relate'):
                            result['toolbar']['relate']=''
                        if result['toolbar'].has_key('print'):
                            new_print = filter(lambda x : x['report_name'] == 'preoffer.report',result['toolbar']['print'])
                            result['toolbar']['print'] =new_print
            else : 
                if result.has_key('toolbar'):
                    if result['toolbar'].has_key('print'):
                        new_print = filter(lambda x : x['report_name'] not in ['offer.model.report','preoffer.report'],result['toolbar']['print'])
                        result['toolbar']['print'] =new_print
        return result
    
    def fields_get(self, cr, uid, fields=None, context=None):
        res = super(dm_offer, self).fields_get(cr, uid, fields, context)
        if context and not context.has_key('type') and res.has_key('type'):
            res['type']['selection'] = [('new','New'),('standart','Standart'),('rewrite','Rewrite')]
        return res
    
    def default_get(self, cr, uid, fields, context=None):
        value = super(dm_offer, self).default_get(cr, uid, fields, context)
        if not context.has_key('create') and context.has_key('type') and context['type']=='model' :
            value['code']=self.pool.get('ir.sequence').get(cr, uid, 'dm.offer')
        return value        

    def create(self,cr,uid,vals,context={}):
        if not vals.has_key('type') and vals.has_key('preoffer_type'):
            vals['type'] = 'preoffer'
        elif not vals.has_key('type') :
            vals['type'] = 'model'
        context['create'] = 'create'
        new_offer_id = super(dm_offer,self).create(cr,uid,vals,context)
        if vals.has_key('preoffer_original_id'):
            self.write(cr,uid,vals['preoffer_original_id'],{'preoffer_offer_id':new_offer_id})
        return new_offer_id
    
    def write(self,cr,uid,ids,vals,context={}):
        if vals.has_key('preoffer_original_id'):
            self.write(cr,uid,vals['preoffer_original_id'],{'preoffer_offer_id':ids[0]})
        return super(dm_offer,self).write(cr,uid,ids,vals,context)
    
    def copy(self, cr, uid, id, default=None, context=None):
        if default is None:
            default = {}
        default = default.copy()
        offer = self.browse(cr,uid,[id])[0]
        default['name']='New offer from model %s' % offer.name
        print default['name']
        default['step_ids']=[]
        #            offer is copied
        offer_id = super(dm_offer, self).copy(cr, uid, id, default, context)
        offer_step_obj = self.pool.get('dm.offer.step')
        offer_step_ids = offer_step_obj.search(cr,uid,[('offer_id','=',id)])
#        print "DEBUG - offer_step_ids : ",offer_step_ids
        offer_steps = offer_step_obj.browse(cr,uid,offer_step_ids)
#        print "DEBUG - offer_steps :",offer_steps
        #            offer step are copied
        new_steps = []
        for step in offer_steps :
            nid = offer_step_obj.copy(cr,uid,step.id,{'offer_id':offer_id,'outgoing_transition_ids':[],'incoming_transition_ids':[]})#,'document_ids':[]})
            new_steps.append({'old_id':step.id,'new_id':nid,'o_trans_id':step.outgoing_transition_ids})
#            print "DEBUG - step :",step
#            print "DEBUG - step transition :",step.outgoing_transition_ids

#        print "DEBUG new_steps : ",new_steps
        #            transitions are copied
        for step in new_steps : 
            if step['o_trans_id']:
                for trans in step['o_trans_id']:
                    step_to =[nid['new_id'] for nid in new_steps if nid['old_id']==trans.step_to.id][0]
                    self.pool.get('dm.offer.step.transition').copy(cr,uid,trans.id,{'step_to':step_to,'step_from':step['new_id']})
        return offer_id

dm_offer()

class dm_offer_translation(osv.osv):
    _name = "dm.offer.translation"
    _rec_name = "offer_id"
    _order = "date"
    _columns = {
        'offer_id' : fields.many2one('dm.offer', 'Offer', required=True),
        'language_id' : fields.many2one('res.lang','Language'),
        'translator_id' : fields.many2one('res.partner', 'Translator'),
        'date' : fields.date('Date'),
        'notes' : fields.text('Notes'),
    }
dm_offer_translation()

#class dm_offer_history(osv.osv):
#    _name = "dm.offer.history"
#    _order = 'date'
#    _columns = {
#        'offer_id' : fields.many2one('dm.offer', 'Offer', required=True, ondelete="cascade"),
#        'date' : fields.date('Date'),
##        'user_id' : fields.many2one('res.users', 'User'),
##        'state': fields.selection(AVAILABLE_STATES, 'Status', size=16)
#        'campaign_id' : fields.many2one('dm.campaign','Name'),
#        'code' : fields.char('Code', size=16),
#        'responsible_id' : fields.many2one('res.users','Responsible'),
#    }
##    _defaults = {
##        'date': lambda *a: time.strftime('%Y-%m-%d'),
##    }
#dm_offer_history()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

