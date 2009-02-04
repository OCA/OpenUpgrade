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
    _inherit = "res.partner"
    _table = "res_partner"
#    _rec_name = "firstname"
    _columns = {
#        'code' : fields.char('Code',size=64),
#        'language_id' : fields.many2one('res.lang','Main Language'),
        'language_ids' : fields.many2many('res.lang','dm_customer_langs','lang_id','customer_id','Other Languages'),
        'prospect_media_ids' : fields.many2many('dm.media','dm_customer_prospect_media','prospect_media_id','customer_id','Prospect for Media'),
        'client_media_ids' : fields.many2many('dm.media','dm_customer_client_media','client_media_id','customer_id','Client for Media'),
        'title' : fields.char('Title',size=32),
#        'firstname' : fields.char('First Name', size=64),
        'lastname' : fields.char('Last Name', size=64),
#        'add1' : fields.char('Address1', size=64),
#        'add2' : fields.char('Address2', size=64),
#        'add3' : fields.char('Address3', size=64),
#        'add4' : fields.char('Address4', size=64),
#        'country_id' : fields.many2one('res.country','Country'),
#        'zip' : fields.char('Zip Code', size=16),
#        'zip_summary' : fields.char('Zip Summary', size=64),
#        'distribution_office' : fields.char('Distribution Office', size=64),
        'decoy_address' : fields.boolean('Decoy Address', help='A decoy address is an address used to identify unleagal uses of a customers file'),
        'decoy_owner' : fields.many2one('res.partner','Decoy Address Owner', help='The partner this decoy address belongs to'),
        'decoy_external_ref' : fields.char('External Reference', size=64, help='The reference of the decoy address for the owner'),
        'decoy_media_ids': fields.many2many('dm.media','dm_decoy_media_rel','decoy_media_id','customer_id','decoy address for Media'),
        'decoy_for_campaign': fields.boolean('Used for Campaigns', help='Define if this decoy address can be used with campaigns'),
        'decoy_for_renting': fields.boolean('Used for File Renting', help='Define if this decoy address can be used with used with customers files renting'),
    }
dm_customer()


class dm_customer_order(osv.osv):
    _name = "dm.customer.order"
    _inherit = "sale.order"
    _table = "sale_order"
    _columns ={
        'customer_id' : fields.many2one('dm.customer', 'Customer', ondelete='cascade'),
        'segment_id' : fields.many2one('dm.campaign.proposition.segment','Segment'),
        'offer_step_id' : fields.many2one('dm.offer.step','Offer Step'),
#        'note' : fields.text('Notes'),
        'state' : fields.selection([('draft','Draft'),('done','Done')], 'Status', readonly=True),
    }
    _defaults = {
        'picking_policy': lambda *a: 'one',
#        'state': lambda *a: 'draft',
    }

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
              customer_id = self.pool.get('dm.customer').create(cr,uid,vals)
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

            workitem.write(cr,uid,workitem_id,vals)
        # create new workitem
        else:
            vals['customer_id']=customer_id
            if segment_id :
                vals['segment_id']=segment_id[0]
            workitem.create(cr,uid,vals)

        self.write(cr,uid,ids,{'state':'done','customer_id':customer_id})
        return True
        """

dm_customer_order()

"""
class dm_workitem(osv.osv):
    _name = "dm.workitem"
    _columns = {
        'step_id' : fields.many2one('dm.offer.step', 'Offer Step',required=True, ondelete="cascade"),
        'segment_id' : fields.many2one('dm.campaign.proposition.segment', 'Segments', required=True, ondelete="cascade"),
        'customer_id' : fields.many2one('dm.customer', 'Customer', ondelete="cascade"),
        'date_next_action' : fields.date('Next Action'),
        'purchase_amount' : fields.float('Amount', digits=(16,2))
    }
    def create(self, cr, uid, vals, context=None, check=True):
        step = self.pool.get('dm.offer.step').browse(cr,uid,[vals['step_id']])[0]
        if step.outgoing_transition_ids:
            transitions = dict(map(lambda x : (x.id,x.delay),step.outgoing_transition_ids))
            trans = [(k,v) for k,v in transitions.items() if v == min(transitions.values())][0]
            new_date = datetime.date.today() + datetime.timedelta(trans[1])
            vals['date_next_action'] = new_date
        return super(dm_offer_step_workitem, self).create(cr, uid, vals, context)

    def _update_workitem(self, cr, uid, ids=False, context={}):
        '''
        Function called by the sceduler to update workitem from the segments of propositions.
        '''
"""
"""
        wrkitem_ids =self.search(cr,uid,[('date_next_action','=',time.strftime('%Y-%m-%d'))])
        wrkitems =self.browse(cr,uid,wrkitem_ids)
        if not wrkitems:
            return
        for wrkitem in wrkitems :
            step = wrkitem.step_id
            if step.outgoing_transition_ids:
                transitions = dict(map(lambda x : (x,int(x.delay)),step.outgoing_transition_ids))
                trans = [k for k,v in transitions.items() if v == min(transitions.values())][0]
                # If relaunching
                if trans.step_to.type == 'RL':
                    prop_id = self.pool.get('dm.campaign.proposition').copy(cr, uid, wrkitem.segment_id.proposition_id.id,
                        {'proposition_type':'relaunching', 'initial_proposition_id':wrkitem.segment_id.proposition_id.id})
                    self.pool.get('dm.campaign.proposition.segment').write(cr, uid, wrkitem.segment_id.id, {'proposition_id':prop_id})
                    re_step_id = self.pool.get('dm.offer.step').search(cr,uid,[('offer_id','=',step.offer_id.id),('flow_start','=',True),('media_id','=',step.media_id.id)])
                    self.write(cr,uid,wrkitem.id,{'step_id':re_step_id[0]}) 
                else :
                    self.write(cr,uid,wrkitem.id,{'step_id':trans.step_to.id})
"""
"""
        return True

dm_workitem()
"""

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
                criteria.append("p.%s %s '%s'"%(i.field.name, i.operator, "%"+i.value+"%"))
        if browse_id.customer_numeric_criteria_ids:
            for i in browse_id.customer_numeric_criteria_ids:
                criteria.append("p.%s %s %f"%(i.field.name, i.operator, i.value))
        if browse_id.customer_boolean_criteria_ids:
            for i in browse_id.customer_boolean_criteria_ids:
                criteria.append("p.%s %s %s"%(i.field.name, i.operator, i.value))
        if browse_id.customer_date_criteria_ids:
            for i in browse_id.customer_date_criteria_ids:
                criteria.append("p.%s %s '%s'"%(i.field.name, i.operator, i.value))
        if browse_id.order_text_criteria_ids:
            for i in browse_id.order_text_criteria_ids:
                criteria.append("s.%s %s '%s'"%(i.field.name, i.operator, "%"+i.value+"%"))
        if browse_id.order_numeric_criteria_ids:
            for i in browse_id.order_numeric_criteria_ids:
                criteria.append("s.%s %s %f"%(i.field.name, i.operator, i.value))
        if browse_id.order_boolean_criteria_ids:
            for i in browse_id.order_boolean_criteria_ids:
                criteria.append("s.%s %s %s"%(i.field.name, i.operator, i.value))
        if browse_id.order_date_criteria_ids:
            for i in browse_id.order_date_criteria_ids:
                criteria.append("s.%s %s '%s'"%(i.field.name, i.operator, i.value))
                
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
#        'field' : fields.many2one('ir.model.fields','Customers Field',
#               domain=['&',('model_id','like','dm.customer'),'!',('model_id','like','dm.customer.order'),
#               '!',('model_id','like','dm.customers_list'),
#               '!',('model_id','like','dm.plugins.value'),
#               ('ttype','like','char')],
#               context={'model':'dm.customer'}),
        'field' : fields.many2one('ir.model.fields','Customers Field',
               domain=[('model_id.model','=','dm.customer'),
               ('ttype','like','char')],
               context={'model':'dm.customer'}),
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
#        'field' : fields.many2one('ir.model.fields','Customers Field',
#               domain=['&',('model_id','like','dm.customer'),'!',('model_id','like','dm.customer.order'),
#               ('ttype','like','integer'),
#               ('ttype','like','float'),
#               '!',('model_id','like','dm.customers_list'),
#               '!',('model_id','like','dm.plugins.value')],
#               context={'model':'dm.customer'}),
        'field' : fields.many2one('ir.model.fields','Customers Field',
               domain=[('model_id.model','=','dm.customer'),
               (('ttype','like','integer') or ('ttype','like','float'))],
               context={'model':'dm.customer'}),
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
#        'field' : fields.many2one('ir.model.fields','Customers Field',
#               domain=['&',('model_id','like','dm.customer'),'!',('model_id','like','dm.customer.order'),
#               '!',('model_id','like','dm.customers_list'),
#               '!',('model_id','like','dm.plugins.value'),
#               ('ttype','like','boolean')],
#               context={'model':'dm.customer'}),
        'field' : fields.many2one('ir.model.fields','Customers Field',
               domain=[('model_id.model','=','dm.customer'),
               ('ttype','like','boolean')],
               context={'model':'dm.customer'}),
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
#        'field' : fields.many2one('ir.model.fields','Customers Field',
#               domain=['&',('model_id','like','dm.customer'),'!',('model_id','like','dm.customer.order'),
#               ('ttype','like','date'),
#               '!',('model_id','like','dm.customers_list'),
#               '!',('model_id','like','dm.plugins.value')],
#               context={'model':'dm.customer'}),
        'field' : fields.many2one('ir.model.fields','Customers Field',
               domain=[('model_id.model','=','dm.customer'),
               (('ttype','like','date') or ('ttype','like','datetime'))],
               context={'model':'dm.customer'}),
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
#        'field' : fields.many2one('ir.model.fields','Customers Field',
#               domain=['&',('model_id','like','dm.customer'),'!',('model_id','like','dm.customer.order'),
#               '!',('model_id','like','dm.customers_list')],
#               context={'model':'dm.customer'}),
        'field' : fields.many2one('ir.model.fields','Customers Field',
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
#         'field' : fields.many2one('ir.model.fields','Customers Field'),
        'field' : fields.many2one('ir.model.fields','Customers Field',
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
        'field' : fields.many2one('ir.model.fields','Customers Field',
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
#        'field' : fields.many2one('ir.model.fields','Customers Field'),
        'field' : fields.many2one('ir.model.fields','Customers Field',
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
#        'user_id' : fields.many2one('res.users', 'User'),
#        'state': fields.selection(AVAILABLE_STATES, 'Status', size=16)
        'campaign_id' : fields.many2one('dm.campaign','Name', ondelete="cascade"),
        'code' : fields.char('Code', size=16),
        'responsible_id' : fields.many2one('res.users','Responsible'),
    }
#    _defaults = {
#        'date': lambda *a: time.strftime('%Y-%m-%d'),
#    }
dm_offer_history()
