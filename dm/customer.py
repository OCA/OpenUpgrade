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

from osv import fields
from osv import osv
import pooler
import sys
import datetime
import netsvc

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


class res_partner(osv.osv):
    _inherit = "res.partner"
    _columns = {
        'language_ids' : fields.many2many('res.lang','dm_customer_langs','lang_id','customer_id','Other Languages'),
        'prospect_media_ids' : fields.many2many('dm.media','dm_customer_prospect_media','prospect_media_id','customer_id','Prospect for Media'),
        'client_media_ids' : fields.many2many('dm.media','dm_customer_client_media','client_media_id','customer_id','Client for Media'),
        'decoy_address' : fields.boolean('Decoy Address', help='A decoy address is an address used to identify unleagal uses of a customers file'),
        'decoy_owner' : fields.many2one('res.partner','Decoy Address Owner', help='The partner this decoy address belongs to'),
        'decoy_external_ref' : fields.char('External Reference', size=64, help='The reference of the decoy address for the owner'),
        'decoy_media_ids': fields.many2many('dm.media','dm_decoy_media_rel','decoy_media_id','customer_id','decoy address for Media'),
        'decoy_for_campaign': fields.boolean('Used for Campaigns', help='Define if this decoy address can be used with campaigns'),
        'decoy_for_renting': fields.boolean('Used for File Renting', help='Define if this decoy address can be used with used with customers files renting'),
    }
res_partner()


class dm_customer_order(osv.osv):
    _name = "dm.customer.order"
    _inherit = "sale.order"
    _table = "sale_order"
    _columns ={
        'customer_id' : fields.many2one('res.partner', 'Customer', ondelete='cascade'),
        'segment_id' : fields.many2one('dm.campaign.proposition.segment','Segment'),
        'offer_step_id' : fields.many2one('dm.offer.step','Offer Step'),
#        'note' : fields.text('Notes'),
        'state' : fields.selection([('draft','Draft'),('done','Done')], 'Status', readonly=True),
    }
    _defaults = {
        'picking_policy': lambda *a: 'one',
#        'state': lambda *a: 'draft',
    }
    def set_confirm(self, cr, uid, ids, *args):
        self.write(cr, uid, ids, {'state': 'done'})
        return True

dm_customer_order()

class dm_customer_gender(osv.osv):
    _name = "dm.customer.gender"
    def _customer_gender_code(self, cr, uid, ids, name, args, context={}):
        result ={}
        for id in ids:
            code=""
            cust_gender = self.browse(cr,uid,[id])[0]
            if cust_gender.lang_id:
                if not cust_gender.from_gender_id:
                    code='_'.join([cust_gender.lang_id.code, cust_gender.to_gender_id.name])
                else:
                    code='_'.join([cust_gender.lang_id.code, 'from', cust_gender.from_gender_id.name, 'to', cust_gender.to_gender_id.name])
            else:
                if not cust_gender.from_gender_id:
                    code=cust_gender.to_gender_id.name
                else:
                    code='_'.join(['from', cust_gender.from_gender_id.name, 'to', cust_gender.to_gender_id.name])
            result[id]=code
        return result

    _columns = {
        'name' : fields.char('Name', size=16),
        'code' : fields.function(_customer_gender_code,string='Code',type='char',method=True,readonly=True),
        'from_gender_id' : fields.many2one('res.partner.title', 'From Gender', domain="[('domain','=','contact')]"),
        'to_gender_id' : fields.many2one('res.partner.title', 'To Gender', required=True, domain="[('domain','=','contact')]"),
        'lang_id' : fields.many2one('res.lang', 'Language'),
        'description' : fields.text('Description'),
    }
dm_customer_gender()

class dm_workitem(osv.osv):
    _name = "dm.workitem"
    _description = "workitem"
    _SOURCES = [('address_id','Partner Address')]
    """
    def create(self,cr,uid,vals,context={}):
        if 'action_time' in vals and vals['action_time']:
            return super(dm_workitem, self).create(cr, uid, vals, context)
        if 'tr_from_id' in vals and vals['tr_from_id']:
            tr = self.pool.get('dm.offer.step.transition').browse(cr, uid, vals['tr_from_id'])
            print "Delay Type: ",tr.delay_type

            wi_action_time = datetime.datetime.now()
            kwargs = {(tr.delay_type+'s'): tr.delay}
            next_action_time = wi_action_time + datetime.timedelta(**kwargs)
            print "Next action date : ",next_action_time
            vals['action_time'] = next_action_time
            print "Vals : ",vals
        else:
            vals['action_time'] = datetime.datetime.now()
            print "Vals : ",vals

        return super(dm_workitem, self).create(cr, uid, vals, context)
    """

    _columns = {
        'step_id' : fields.many2one('dm.offer.step', 'Offer Step', select="1", ondelete="cascade"),
        'segment_id' : fields.many2one('dm.campaign.proposition.segment', 'Segments', select="1", ondelete="cascade"),
        'address_id' : fields.many2one('res.partner.address', 'Customer Address', select="1", ondelete="cascade"),
        'action_time' : fields.datetime('Action Time'),
        'source' : fields.selection(_SOURCES, 'Source', required=True),
        'error_msg' : fields.text('System Message'),
        'tr_from_id' : fields.many2one('dm.offer.step.transition', 'Source Transition'),
        'state' : fields.selection([('pending','Pending'),('error','Error'),('cancel','Cancelled'),('done','Done')], 'Status'),
    }
    _defaults = {
        'source': lambda *a: 'address_id',
        'state': lambda *a: 'pending',
    }

    def run(self, cr, uid, wi, context={}):
        print "Calling run"
        context['active_id'] = wi.id
        done = False
        try:
            server_obj = self.pool.get('ir.actions.server')
            print "Calling run for : ",wi.step_id.action_id.server_action_id.name
            res = True

            """ Check if action must be done or cancelled """
            """
            for tr in wi.step_id.outgoing_transition_ids:
                eval_context = {
                    'pool' : self.pool,
                    'cr' : cr,
                    'uid' : uid,
                    'wi': wi,
                    'tr':tr,
                }
                val = {}
                print "Outgoing Action Condition : ",tr.condition_id.out_act_cond
                try:
                    exec tr.condition_id.out_act_cond.replace('\r','') in eval_context,val
                    print "Val out get wi_ids : ",val.get('wi_ids',False)
                    print "Val out get res : ",val.get('result',False)
                except Exception,e:
                    netsvc.Logger().notifyChannel('dm', netsvc.LOG_ERROR, 'Invalid code in Outgoing Action Condition: %s'% tr.condition_id.out_act_cond)
                    netsvc.Logger().notifyChannel('dm', netsvc.LOG_ERROR, e)
                    continue
                if not val.get('result',False):
                    res = False
                    act_step = tr.step_to_id.name or False
                    break
            """
            """ Check Incoming transitions Action condition """
#            if not res:
            for tr in wi.step_id.incoming_transition_ids:
                eval_context = {
                    'pool' : self.pool,
                    'cr' : cr,
                    'uid' : uid,
                    'wi': wi,
                    'tr':tr,
                }
                val = {}
                print "Incoming Transition : ",tr.condition_id.name
                print "Incoming Action Condition : ",tr.condition_id.in_act_cond
                try:
                    exec tr.condition_id.in_act_cond.replace('\r','') in eval_context,val
                    print "Val in get step_to_check: ",val.get('step_to_check',False)
                    print "Val in get wid_ids : ",val.get('wi_ids',False)
                    print "Val in get res : ",val.get('result',False)
                except Exception,e:
                    netsvc.Logger().notifyChannel('dm', netsvc.LOG_ERROR, 'Invalid code in Incoming Action Condition: %s'% tr.condition_id.in_act_cond)
                    netsvc.Logger().notifyChannel('dm', netsvc.LOG_ERROR, e)
                    continue
                if not val.get('result',False):
                    res = False
                    act_step = tr.step_from_id.name or False
                    break

            if res:
                res = server_obj.run(cr, uid, [wi.step_id.action_id.server_action_id.id], context)
                self.write(cr, uid, [wi.id], {'state': 'done','error_msg':""})
                done = True
            else:
                self.write(cr, uid, [wi.id], {'state': 'cancel','error_msg':'Cancelled by : %s'% act_step})
                done = False
        except :
            self.write(cr, uid, [wi.id], {'state': 'error','error_msg':sys.exc_info()})

        if done:
            """ Create next auto workitems """
            for tr in wi.step_id.outgoing_transition_ids:
                print "Delay Type: ",tr.delay_type

                wi_action_time = datetime.datetime.strptime(wi.action_time, '%Y-%m-%d  %H:%M:%S')
                kwargs = {(tr.delay_type+'s'): tr.delay}
                next_action_time = wi_action_time + datetime.timedelta(**kwargs)
                print "Next action date : ",next_action_time

                aw_id = self.copy(cr, uid, wi.id, {'step_id':tr.step_to_id.id, 'action_time':next_action_time})
                print "auto wi : ",aw_id
        return True

    def __init__(self, *args):
        self.is_running = False
        return super(dm_workitem, self).__init__(*args)

    def check_all(self, cr, uid, context={}):
        print "Calling check all"
        if not self.is_running:
            self.is_running = True
            ids = self.search(cr, uid, [('state','=','pending'),
                ('action_time','<=',time.strftime('%Y-%m-%d %H:%M:%S'))])
            print "WI to process : ",ids
            for wi in self.browse(cr, uid, ids, context=context):
                self.run(cr, uid, wi, context=context)
            self.is_running = False
        return True
dm_workitem()

class dm_customer_segmentation(osv.osv):
    _name = "dm.customer.segmentation"
    _description = "Segmentation"

    _columns = {
        'name' : fields.char('Name', size=64, required=True),
        'code' : fields.char('Code', size=32, required=True),
        'notes' : fields.text('Description'),
        'sql_query' : fields.text('SQL Query'),
        'customer_text_criteria_ids' : fields.one2many('dm.customer.text_criteria', 'segmentation_id', 'Customers Textual Criteria'),
        'customer_numeric_criteria_ids' : fields.one2many('dm.customer.numeric_criteria', 'segmentation_id', 'Customers Numeric Criteria'),
        'customer_boolean_criteria_ids' : fields.one2many('dm.customer.boolean_criteria', 'segmentation_id', 'Customers Boolean Criteria'),
        'customer_date_criteria_ids' : fields.one2many('dm.customer.date_criteria', 'segmentation_id', 'Customers Date Criteria'),
        'order_text_criteria_ids' : fields.one2many('dm.customer.order.text_criteria', 'segmentation_id', 'Customers Order Textual Criteria'),
        'order_numeric_criteria_ids' : fields.one2many('dm.customer.order.numeric_criteria', 'segmentation_id', 'Customers Order Numeric Criteria'),
        'order_boolean_criteria_ids' : fields.one2many('dm.customer.order.boolean_criteria', 'segmentation_id', 'Customers Order Boolean Criteria'),
        'order_date_criteria_ids' : fields.one2many('dm.customer.order.date_criteria', 'segmentation_id', 'Customers Order Date Criteria'),
    }

    def set_customer_criteria(self, cr, uid, id, context={}):
        criteria=[]
        browse_id = self.browse(cr, uid, id)
        if browse_id.customer_text_criteria_ids:
            for i in browse_id.customer_text_criteria_ids:
                criteria.append("p.%s %s '%s'"%(i.field_id.name, i.operator, "%"+i.value+"%"))
        if browse_id.customer_numeric_criteria_ids:
            for i in browse_id.customer_numeric_criteria_ids:
                criteria.append("p.%s %s %f"%(i.field_id.name, i.operator, i.value))
        if browse_id.customer_boolean_criteria_ids:
            for i in browse_id.customer_boolean_criteria_ids:
                criteria.append("p.%s %s %s"%(i.field_id.name, i.operator, i.value))
        if browse_id.customer_date_criteria_ids:
            for i in browse_id.customer_date_criteria_ids:
                criteria.append("p.%s %s '%s'"%(i.field_id.name, i.operator, i.value))
        if browse_id.order_text_criteria_ids:
            for i in browse_id.order_text_criteria_ids:
                criteria.append("s.%s %s '%s'"%(i.field_id.name, i.operator, "%"+i.value+"%"))
        if browse_id.order_numeric_criteria_ids:
            for i in browse_id.order_numeric_criteria_ids:
                criteria.append("s.%s %s %f"%(i.field_id.name, i.operator, i.value))
        if browse_id.order_boolean_criteria_ids:
            for i in browse_id.order_boolean_criteria_ids:
                criteria.append("s.%s %s %s"%(i.field_id.name, i.operator, i.value))
        if browse_id.order_date_criteria_ids:
            for i in browse_id.order_date_criteria_ids:
                criteria.append("s.%s %s '%s'"%(i.field_id.name, i.operator, i.value))

        if criteria:
            sql_query = ("""select distinct p.name \nfrom res_partner p, sale_order s\nwhere p.id = s.customer_id and %s\n""" % (' and '.join(criteria))).replace('isnot','is not')
        else:
            sql_query = """select distinct p.name \nfrom res_partner p, sale_order s\nwhere p.id = s.customer_id"""
        return super(dm_customer_segmentation,self).write(cr, uid, id, {'sql_query':sql_query})

    def create(self,cr,uid,vals,context={}):
        id = super(dm_customer_segmentation,self).create(cr,uid,vals,context)
        self.set_customer_criteria(cr, uid, id)
        return id

    def write(self, cr, uid, ids, vals, context=None):
        id = super(dm_customer_segmentation,self).write(cr, uid, ids, vals, context)
        for i in ids:
            self.set_customer_criteria(cr, uid, i)
        return id

dm_customer_segmentation()

TEXT_OPERATORS = [
    ('like','like'),
    ('ilike','ilike'),
]

NUMERIC_OPERATORS = [
    ('=','equals'),
    ('<','smaller then'),
    ('>','bigger then'),
]

BOOL_OPERATORS = [
    ('is','is'),
    ('isnot','is not'),
]

DATE_OPERATORS = [
    ('=','equals'),
    ('<','before'),
    ('>','after'),
]

class dm_customer_text_criteria(osv.osv):
    _name = "dm.customer.text_criteria"
    _description = "Customer Segmentation Textual Criteria"
    _rec_name = "segmentation_id"

    _columns = {
        'segmentation_id' : fields.many2one('dm.customer.segmentation', 'Segmentation'),
        'field_id' : fields.many2one('ir.model.fields','Customers Field',
               domain=[('model_id.model','=','res.partner'),
               ('ttype','like','char')],
               context={'model':'res.partner'}),
        'operator' : fields.selection(TEXT_OPERATORS, 'Operator', size=32),
        'value' : fields.char('Value', size=128),
    }
dm_customer_text_criteria()

class dm_customer_numeric_criteria(osv.osv):
    _name = "dm.customer.numeric_criteria"
    _description = "Customer Segmentation Numeric Criteria"
    _rec_name = "segmentation_id"

    _columns = {
        'segmentation_id' : fields.many2one('dm.customer.segmentation', 'Segmentation'),
        'field_id' : fields.many2one('ir.model.fields','Customers Field',
               domain=[('model_id.model','=','res.partner'),
               (('ttype','like','integer') or ('ttype','like','float'))],
               context={'model':'res.partner'}),
        'operator' : fields.selection(NUMERIC_OPERATORS, 'Operator', size=32),
        'value' : fields.float('Value', digits=(16,2)),
    }
dm_customer_numeric_criteria()

class dm_customer_boolean_criteria(osv.osv):
    _name = "dm.customer.boolean_criteria"
    _description = "Customer Segmentation Boolean Criteria"
    _rec_name = "segmentation_id"

    _columns = {
        'segmentation_id' : fields.many2one('dm.customer.segmentation', 'Segmentation'),
        'field_id' : fields.many2one('ir.model.fields','Customers Field',
               domain=[('model_id.model','=','res.partner'),
               ('ttype','like','boolean')],
               context={'model':'res.partner'}),
        'operator' : fields.selection(BOOL_OPERATORS, 'Operator', size=32),
        'value' : fields.selection([('true','True'),('false','False')],'Value'),
    }
dm_customer_boolean_criteria()

class dm_customer_date_criteria(osv.osv):
    _name = "dm.customer.date_criteria"
    _description = "Customer Segmentation Date Criteria"
    _rec_name = "segmentation_id"

    _columns = {
        'segmentation_id' : fields.many2one('dm.customer.segmentation', 'Segmentation'),
        'field_id' : fields.many2one('ir.model.fields','Customers Field',
               domain=[('model_id.model','=','res.partner'),
               (('ttype','like','date') or ('ttype','like','datetime'))],
               context={'model':'res.partner'}),
        'operator' : fields.selection(DATE_OPERATORS, 'Operator', size=32),
        'value' : fields.date('Date'),
    }
dm_customer_date_criteria()

class dm_customer_order_text_criteria(osv.osv):
    _name = "dm.customer.order.text_criteria"
    _description = "Customer Order Segmentation Textual Criteria"
    _rec_name = "segmentation_id"

    _columns = {
        'segmentation_id' : fields.many2one('dm.customer.segmentation', 'Segmentation'),
        'field_id' : fields.many2one('ir.model.fields','Customers Field',
               domain=[('model_id.model','=','dm.customer.order'),
               ('ttype','like','char')],
               context={'model':'dm.customer.order'}),
        'operator' : fields.selection(TEXT_OPERATORS, 'Operator', size=32),
        'value' : fields.char('Value', size=128),
    }
dm_customer_order_text_criteria()

class dm_customer_order_numeric_criteria(osv.osv):
    _name = "dm.customer.order.numeric_criteria"
    _description = "Customer Order Segmentation Numeric Criteria"
    _rec_name = "segmentation_id"

    _columns = {
        'segmentation_id' : fields.many2one('dm.customer.segmentation', 'Segmentation'),
        'field_id' : fields.many2one('ir.model.fields','Customers Field',
               domain=[('model_id.model','=','dm.customer.order'),
               (('ttype','like','integer') or ('ttype','like','float'))],
               context={'model':'dm.customer.order'}),
        'operator' : fields.selection(NUMERIC_OPERATORS, 'Operator', size=32),
        'value' : fields.float('Value', digits=(16,2)),
    }
dm_customer_order_numeric_criteria()

class dm_customer_order_boolean_criteria(osv.osv):
    _name = "dm.customer.order.boolean_criteria"
    _description = "Customer Order Segmentation Boolean Criteria"
    _rec_name = "segmentation_id"

    _columns = {
        'segmentation_id' : fields.many2one('dm.customer.segmentation', 'Segmentation'),
        'field_id' : fields.many2one('ir.model.fields','Customers Field',
               domain=[('model_id.model','=','dm.customer.order'),
               ('ttype','like','boolean')],
               context={'model':'dm.customer.order'}),
        'operator' : fields.selection(BOOL_OPERATORS, 'Operator', size=32),
        'value' : fields.selection([('true','True'),('false','False')],'Value'),
    }
dm_customer_order_boolean_criteria()

class dm_customer_order_date_criteria(osv.osv):
    _name = "dm.customer.order.date_criteria"
    _description = "Customer Order Segmentation Date Criteria"
    _rec_name = "segmentation_id"

    _columns = {
        'segmentation_id' : fields.many2one('dm.customer.segmentation', 'Segmentation'),
        'field_id' : fields.many2one('ir.model.fields','Customers Field',
               domain=[('model_id.model','=','dm.customer.order'),
               (('ttype','like','date') or ('ttype','like','datetime'))],
               context={'model':'dm.customer.order'}),
        'operator' : fields.selection(DATE_OPERATORS, 'Operator', size=32),
        'value' : fields.date('Date'),
    }
dm_customer_order_date_criteria()

class dm_offer_history(osv.osv):
    _name = "dm.offer.history"
    _order = 'date'
    _columns = {
        'offer_id' : fields.many2one('dm.offer', 'Offer', required=True, ondelete="cascade"),
        'date' : fields.date('Drop Date'),
        'campaign_id' : fields.many2one('dm.campaign','Name', ondelete="cascade"),
        'code' : fields.char('Code', size=16),
        'responsible_id' : fields.many2one('res.users','Responsible'),
    }
dm_offer_history()

class dm_event(osv.osv_memory):
    _name = "dm.event"
    _rec_name = "campaign_id"
    _columns = {
        'campaign_id' : fields.many2one('dm.campaign', 'Campaign'),
        'segment_id' : fields.many2one('dm.campaign.proposition.segment', 'Segment', required=True),
        'step_id' : fields.many2one('dm.offer.step', 'Offer Step', required=True),
        'source' : fields.selection([('address_id','Addresses')], 'Source', required=True),
        'address_id' : fields.many2one('res.partner.address', 'Address'),
        'trigger_type_id' : fields.many2one('dm.offer.step.transition.trigger','Trigger Condition',required=True),
    }
    _defaults = {
        'source': lambda *a: 'address_id',
    }

    def create(self,cr,uid,vals,context={}):
#        if 'action_time' in vals and vals['action_time']:
#            return super(dm_workitem, self).create(cr, uid, vals, context)
#        if 'trigger_type_id' in vals and vals['trigger_type_id']:
        tr_ids = self.pool.get('dm.offer.step.transition').search(cr, uid, [('step_from_id','=',vals['step_id']),
                ('condition_id','=',vals['trigger_type_id'])])
        for tr in self.pool.get('dm.offer.step.transition').browse(cr, uid, tr_ids):
            wi_action_time = datetime.datetime.now()
            kwargs = {(tr.delay_type+'s'): tr.delay}
            next_action_time = wi_action_time + datetime.timedelta(**kwargs)
            print "Next action date : ",next_action_time
#                vals['action_time'] = next_action_time
            print "Vals : ",vals
#        else:
#            vals['action_time'] = datetime.datetime.now()
#            print "Vals : ",vals

            self.pool.get('dm.workitem').create(cr, uid, {'step_id':tr.step_to_id.id or False, 'segment_id':vals['segment_id'] or False,
            (vals['source']):vals[(vals['source'])] or False, 'action_time':next_action_time, 'source':vals['source']})

        return super(dm_event,self).create(cr,uid,vals,context)

dm_event()
