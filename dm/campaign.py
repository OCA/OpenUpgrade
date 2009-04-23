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
import datetime
import warnings
import netsvc
from mx import DateTime

from osv import fields
from osv import osv


class dm_overlay_payment_rule(osv.osv):
    _name = 'dm.overlay.payment_rule'
    _rec_name = 'journal_id'
    _columns = {
        'journal_id': fields.many2one('account.journal','Journal'),
        'move': fields.selection([('Credit','credit'),('Debit','debit')],'Move'),
        'currency_id':fields.many2one('res.currency','Currency'),
        'country_id':fields.many2one('res.country','Country'),
        'account_id':fields.many2one('account.account','Account'),
        'country_default':fields.boolean('Default for Country')
    }

dm_overlay_payment_rule()

class dm_campaign_group(osv.osv):
    _name = "dm.campaign.group"
    
    def _quantity_planned_total(self, cr, uid, ids, name, args, context={}):
        result={}
        numeric=True
        quantity=0
        groups = self.browse(cr,uid,ids)
        for group in groups:
            for campaign in group.campaign_ids:
                quantity=0
                numeric=True
                if campaign.quantity_planned_total.isdigit():
                    quantity += int(campaign.quantity_planned_total)
                else:
                    result[group.id]='Check Segments'
                    numeric=False
                    break
            if numeric:
                result[group.id]=str(quantity)
        return result

    def _quantity_wanted_total(self, cr, uid, ids, name, args, context={}):
        result={}
        numeric=True
        quantity=0
        groups = self.browse(cr,uid,ids)
        for group in groups:
            for campaign in group.campaign_ids:
                quantity=0
                numeric=True
                if campaign.quantity_wanted_total.isdigit():
                    quantity += int(campaign.quantity_wanted_total)
                elif campaign.quantity_wanted_total == "AAA for a Segment":
                    result[group.id]='AAA for a Segment'
                    numeric=False
                    break
                else:
                    result[group.id]='Check Segments'
                    numeric=False
                    break
            if numeric:
                result[group.id]=str(quantity)
        return result

    def _quantity_delivered_total(self, cr, uid, ids, name, args, context={}):
        result={}
        numeric=True
        quantity=0
        groups = self.browse(cr,uid,ids)
        for group in groups:
            for campaign in group.campaign_ids:
                quantity=0
                numeric=True
                if campaign.quantity_delivered_total.isdigit():
                    quantity += int(campaign.quantity_delivered_total)
                else:
                    result[group.id]='Check Segments'
                    numeric=False
                    break
            if numeric:
                result[group.id]=str(quantity)
        return result

    def _quantity_usable_total(self, cr, uid, ids, name, args, context={}):
        result={}
        quantity=0
        numeric=True
        groups = self.browse(cr,uid,ids)
        for group in groups:
            for campaign in group.campaign_ids:
                quantity=0
                numeric=True
                if campaign.quantity_usable_total.isdigit():
                    quantity += int(campaign.quantity_usable_total)
                else:
                    result[group.id]='Check Segments'
                    numeric=False
                    break
            if numeric:
                result[group.id]=str(quantity)
        return result

    def _camp_group_code(self, cr, uid, ids, name, args, context={}):
        result ={}
        offer_code = ''
        offer_name = ''
        for id in ids:

            dt = time.strftime('%Y-%m-%d')
            date = dt.split('-')
            year = month = ''
            if len(date)==3:
                year = date[0][2:]
                month = date[1]
            final_date=year+month
            grp = self.browse(cr,uid,id)
            for c in grp.campaign_ids:
                if c.offer_id:
                    d = self.pool.get('dm.offer').browse(cr, uid, c.offer_id.id)
                    offer_code = d.code
                    offer_name = d.name
            code1='-'.join([final_date,offer_code, offer_name])
            result[id]=code1
        return result

    _columns = {
        'name': fields.char('Campaign group name', size=64, required=True),
        'code' : fields.function(_camp_group_code,string='Code',type='char',method=True,readonly=True),
        'project_id' : fields.many2one('project.project', 'Project', readonly=True),
        'campaign_ids': fields.one2many('dm.campaign', 'campaign_group_id', 'Campaigns', domain=[('campaign_group_id','=',False)], readonly=True),
        'purchase_line_ids': fields.one2many('dm.campaign.purchase_line', 'campaign_group_id', 'Purchase Lines'),
#        'quantity_planned_total' : fields.function(_quantity_planned_total, string='Total planned Quantity',type="char",size="64",method=True,readonly=True),
        'quantity_wanted_total' : fields.function(_quantity_wanted_total, string='Total Wanted Quantity',type="char",size=64,method=True,readonly=True),
        'quantity_delivered_total' : fields.function(_quantity_delivered_total, string='Total Delivered Quantity',type="char",size=64,method=True,readonly=True),
        'quantity_usable_total' : fields.function(_quantity_usable_total, string='Total Usable Quantity',type="char",size=64,method=True,readonly=True),
    }
dm_campaign_group()


class dm_campaign_type(osv.osv):
    _name = "dm.campaign.type"
    _columns = {
        'name': fields.char('Description', size=64, translate=True, required=True),
        'code': fields.char('Code', size=16, translate=True, required=True),
        'description': fields.text('Description', translate=True),
    }
dm_campaign_type()


class dm_overlay(osv.osv):
    _name = 'dm.overlay'
    _rec_name = 'trademark_id'

    def _overlay_code(self, cr, uid, ids, name, args, context={}):
        result ={}
        for id in ids:

            overlay = self.browse(cr,uid,id)
            trademark_code = overlay.trademark_id.code or ''
            dealer_code = overlay.dealer_id.ref or ''
            code1='-'.join([trademark_code, dealer_code])
            result[id]=code1
        return result

    _columns = {
        'code' : fields.function(_overlay_code,string='Code',type='char',method=True,readonly=True),
        'trademark_id' : fields.many2one('dm.trademark', 'Trademark', required=True),
        'dealer_id' : fields.many2one('res.partner', 'Dealer', domain=[('category_id','ilike','Dealer')], context={'category':'Dealer'}, required=True),
        'country_ids' : fields.many2many('res.country', 'overlay_country_rel', 'overlay_id', 'country_id', 'Country', required=True),
        'bank_account_id' : fields.many2one('account.account', 'Account'),
        'payment_method_rule_ids':fields.many2many('dm.overlay.payment_rule','overlay_payment_method_rule_rel','overlay_id','payment_rule_id','Payment Method Rules')
    }
dm_overlay()

class one2many_mod_task(fields.one2many):
    def get(self, cr, obj, ids, name, user=None, offset=0, context=None, values=None):
        if not context:
            context = {}
        if not values:
             values = {}
        res = {}
        for id in ids:
            res[id] = []
        for id in ids:
            query = "select project_id from dm_campaign where id = %i" %id
            cr.execute(query)
            project_ids = [ x[0] for x in cr.fetchall()]
            if name[0] == 'd':
                ids2 = obj.pool.get(self._obj).search(cr, user, [(self._fields_id,'in',project_ids),('type','=','DTP')], limit=self._limit)
            elif name[0] == 'm':
                ids2 = obj.pool.get(self._obj).search(cr, user, [(self._fields_id,'in',project_ids),('type','=','Mailing Manufacturing')], limit=self._limit)
            elif name[0] == 'c':
                ids2 = obj.pool.get(self._obj).search(cr, user, [(self._fields_id,'in',project_ids),('type','=','Customers List')], limit=self._limit)
            elif name[0] == 'i':
                ids2 = obj.pool.get(self._obj).search(cr, user, [(self._fields_id,'in',project_ids),('type','=','Items Procurement')], limit=self._limit)
            else :
                ids2 = obj.pool.get(self._obj).search(cr, user, [(self._fields_id,'in',project_ids),('type','=','Mailing Manufacturing')], limit=self._limit)
            for r in obj.pool.get(self._obj)._read_flat(cr, user, ids2, [self._fields_id], context=context, load='_classic_write'):
                res[id].append( r['id'] )
        return res 

class one2many_mod_pline(fields.one2many):
    def get(self, cr, obj, ids, name, user=None, offset=0, context=None, values=None):
        if not context:
            context = {}
        if not values:
                values = {}
        res = {}
        for id in ids:
            res[id] = []
        cr.execute("select id from product_category where name='Direct Marketing'")
        direct_id = cr.fetchone()
        sql="select id,name from product_category where parent_id=%d" %direct_id
        cr.execute(sql)
        res_type = cr.fetchall()
        type={}
        for x in res_type:
            type[x[1]]=x[0]
        for id in ids:
            if name[0] == 'd':
                ids2 = obj.pool.get(self._obj).search(cr, user, [('campaign_id','=',id),('product_category','=',type['DTP'])], limit=self._limit)
            elif name[0] == 'm':
                ids2 = obj.pool.get(self._obj).search(cr, user, [('campaign_id','=',id),('product_category','=',type['Mailing Manufacturing'])], limit=self._limit)
            elif name[0] == 'c':
                ids2 = obj.pool.get(self._obj).search(cr, user, [('campaign_id','=',id),('product_category','=',type['Customers List'])], limit=self._limit)
            elif name[0] == 'i':
                ids2 = obj.pool.get(self._obj).search(cr, user, [('campaign_id','=',id),('product_category','=',type['Items'])], limit=self._limit)
            else :
                ids2 = obj.pool.get(self._obj).search(cr, user, [('campaign_id','=',id),('product_category','=',type['Mailing Manufacturing'])], limit=self._limit)
            for r in obj.pool.get(self._obj)._read_flat(cr, user, ids2, [self._fields_id], context=context, load='_classic_write'):
                res[id].append( r['id'] )
        return res

class dm_campaign(osv.osv):
    _name = "dm.campaign"
    _inherits = {'account.analytic.account': 'analytic_account_id'}
    _rec_name = 'name'

    def dtp_making_time_get(self, cr, uid, ids, name, arg, context={}):
        result={}
        for i in ids:
            result[i]=0.0
        return result

    def _campaign_code(self, cr, uid, ids, name, args, context={}):
        result ={}
        for id in ids:
            camp = self.browse(cr,uid,[id])[0]
            offer_code = camp.offer_id and camp.offer_id.code or ''
            trademark_code = camp.trademark_id and camp.trademark_id.code or ''
            dealer_code =camp.dealer_id and camp.dealer_id.ref or ''
            date_start = camp.date_start or ''
            country_code = camp.country_id.code or ''
            date = date_start.split('-')
            year = month = ''
            if len(date)==3:
                year = date[0][2:]
                month = date[1]
            final_date=month+year
            code1='-'.join([offer_code ,dealer_code ,trademark_code ,final_date ,country_code])
            result[id]=code1
        return result

    def onchange_lang_currency(self, cr, uid, ids, country_id):
        value = {}
        if country_id:
            country = self.pool.get('res.country').browse(cr,uid,[country_id])[0]
            value['lang_id'] =  country.main_language.id
            value['currency_id'] = country.main_currency.id
            value['forwarding_charge'] = country.forwarding_charge
        else:
            value['lang_id']=0
            value['currency_id']=0
            value['forwarding_charge'] = 0.0
        return {'value':value}

    def _quantity_planned_total(self, cr, uid, ids, name, args, context={}):
        result={}
        campaigns = self.browse(cr,uid,ids)
        for campaign in campaigns:
            quantity=0
            numeric=True
            for propo in campaign.proposition_ids:
                if propo.quantity_planned:
                    quantity += propo.quantity_planned
            result[campaign.id]=str(quantity)
        return result

    def _quantity_wanted_total(self, cr, uid, ids, name, args, context={}):
        result={}
        campaigns = self.browse(cr,uid,ids)
        for campaign in campaigns:
            quantity=0
            numeric=True
            for propo in campaign.proposition_ids:
                if propo.quantity_wanted.isdigit():
                    quantity += int(propo.quantity_wanted)
                elif propo.quantity_wanted == "AAA for a Segment":
                    result[campaign.id]='AAA for a Segment'
                    numeric=False
                    break
                else:
                    result[campaign.id]='Check Segments'
                    numeric=False
                    break
            if numeric:
                result[campaign.id]=str(quantity)
        return result

    def _quantity_delivered_total(self, cr, uid, ids, name, args, context={}):
        result={}
        campaigns = self.browse(cr,uid,ids)
        for campaign in campaigns:
            quantity=0
            numeric=True
            for propo in campaign.proposition_ids:
                if propo.quantity_delivered.isdigit():
                    quantity += int(propo.quantity_delivered)
                else:
                    result[campaign.id]='Check Segments'
                    numeric=False
                    break
            if numeric:
                result[campaign.id]=str(quantity)
        return result

    def _quantity_usable_total(self, cr, uid, ids, name, args, context={}):
        result={}
        campaigns = self.browse(cr,uid,ids)
        for campaign in campaigns:
            quantity=0
            numeric=True
            for propo in campaign.proposition_ids:
                if propo.quantity_usable.isdigit():
                    quantity += int(propo.quantity_usable)
                else:
                    result[campaign.id]='Check Segments'
                    numeric=False
                    break
            if numeric:
                result[campaign.id]=str(quantity)
        return result


    _columns = {
        'code1' : fields.function(_campaign_code,string='Code',type="char",size=64,method=True,readonly=True),
        'offer_id' : fields.many2one('dm.offer', 'Offer',domain=[('state','in',['ready','open']),('type','in',['new','standart','rewrite'])], required=True,
            help="Choose the commercial offer to use with this campaign, only offers in ready to plan or open state can be assigned"),
        'country_id' : fields.many2one('res.country', 'Country',required=True, 
            help="The language and currency will be automaticaly assigned if they are defined for the country"),
        'lang_id' : fields.many2one('res.lang', 'Language'),
        'trademark_id' : fields.many2one('dm.trademark', 'Trademark'),
        'project_id' : fields.many2one('project.project', 'Project', readonly=True,
            help="Generating the Retro Planning will create and assign the different tasks used to plan and manage the campaign"),
        'campaign_group_id' : fields.many2one('dm.campaign.group', 'Campaign group'),
        'notes' : fields.text('Notes'),
        'proposition_ids' : fields.one2many('dm.campaign.proposition', 'camp_id', 'Proposition'),
        'campaign_type_id' : fields.many2one('dm.campaign.type','Type'),
        'analytic_account_id' : fields.many2one('account.analytic.account','Analytic Account', ondelete='cascade'),
        'planning_state' : fields.selection([('pending','Pending'),('inprogress','In Progress'),('done','Done')], 'Planning Status',readonly=True),
        'dtp_state' : fields.selection([('pending','Pending'),('inprogress','In Progress'),('done','Done')], 'DTP Status',readonly=True),
        'items_state' : fields.selection([('pending','Pending'),('inprogress','In Progress'),('done','Done')], 'Items Status',readonly=True),
        'translation_state' : fields.selection([('pending','Pending'),('inprogress','In Progress'),('done','Done')], 'Translation Status',readonly=True),
        'manufacturing_state' : fields.selection([('pending','Pending'),('inprogress','In Progress'),('done','Done')], 'Manufacturing Status',readonly=True),
        'customer_file_state' : fields.selection([('pending','Pending'),('inprogress','In Progress'),('done','Done')], 'Customers Files Status',readonly=True),
        'dealer_id' : fields.many2one('res.partner', 'Dealer',domain=[('category_id','ilike','Dealer')], context={'category':'Dealer'},
            help="The dealer is the partner the campaign is planned for"),
        'responsible_id' : fields.many2one('res.users','Responsible'),
        'manufacturing_responsible_id' : fields.many2one('res.users','Responsible'),
        'dtp_responsible_id' : fields.many2one('res.users','Responsible'),
        'files_responsible_id' : fields.many2one('res.users','Responsible'),
        'item_responsible_id' : fields.many2one('res.users','Responsible'),
#        'invoiced_partner_id' : fields.many2one('res.partner','Invoiced Partner'),
#        'files_delivery_address_id' : fields.many2one('res.partner.address','Delivery Address'),
        'dtp_making_time' : fields.function(dtp_making_time_get, method=True, type='float', string='Making Time'),
        'deduplicator_id' : fields.many2one('res.partner','Deduplicator',domain=[('category_id','ilike','Deduplicator')], context={'category':'Deduplicator'},
            help="The deduplicator is a partner responsible to remove identical addresses from the customers list"),
        'cleaner_id' : fields.many2one('res.partner','Cleaner',domain=[('category_id','ilike','Cleaner')], context={'category':'Cleaner'},
            help="The cleaner is a partner responsible to remove bad addresses from the customers list"),
        'currency_id' : fields.many2one('res.currency','Currency',ondelete='cascade'),
        'manufacturing_cost_ids': fields.one2many('dm.campaign.manufacturing_cost','campaign_id','Manufacturing Costs'),
        'manufacturing_product_id': fields.many2one('product.product','Manufacturing Product'),
        'overlay_id': fields.many2one('dm.overlay', 'Overlay'),
        'router_id' : fields.many2one('res.partner', 'Router',domain=[('category_id','ilike','Router')], context={'category':'Router'},
            help="The router is the partner who will send the mailing to the final customer"),
        'dtp_task_ids': one2many_mod_task('project.task', 'project_id', "DTP tasks",
                                                        domain=[('type','ilike','DTP')], context={'type':'DTP'}),
        'manufacturing_task_ids': one2many_mod_task('project.task', 'project_id', "Manufacturing tasks",
                                                        domain=[('type','ilike','Mailing Manufacturing')],context={'type':'Mailing Manufacturing'}),
        'cust_file_task_ids': one2many_mod_task('project.task', 'project_id', "Customer Files tasks",
                                                        domain=[('type','ilike','Customers List')], context={'type':'Customers List'}),
        'item_task_ids': one2many_mod_task('project.task', 'project_id', "Items Procurement tasks",
                                                        domain=[('type','ilike','Items Procurement')], context={'type':'Items Procurement'}),
        'quantity_planned_total' : fields.function(_quantity_planned_total, string='Total planned Quantity',type="char",size=64,method=True,readonly=True),
        'quantity_wanted_total' : fields.function(_quantity_wanted_total, string='Total Wanted Quantity',type="char",size=64,method=True,readonly=True),
        'quantity_delivered_total' : fields.function(_quantity_delivered_total, string='Total Delivered Quantity',type="char",size=64,method=True,readonly=True),
        'quantity_usable_total' : fields.function(_quantity_usable_total, string='Total Usable Quantity',type="char",size=64,method=True,readonly=True),
        'dtp_purchase_line_ids': one2many_mod_pline('dm.campaign.purchase_line', 'campaign_id', "DTP Purchase Lines",
                                                        domain=[('product_category','=','DTP')], context={'product_category':'DTP'}),
        'manufacturing_purchase_line_ids': one2many_mod_pline('dm.campaign.purchase_line', 'campaign_id', "Manufacturing Purchase Lines",
                                                        domain=[('product_category','=','Mailing Manufacturing')],
                                                        context={'product_category':'Mailing Manufacturing'}),
        'cust_file_purchase_line_ids': one2many_mod_pline('dm.campaign.purchase_line', 'campaign_id', "Customer Files Purchase Lines",
                                                        domain=[('product_category','=','Customers List')], context={'product_category':'Customers List'}),
        'item_purchase_line_ids': one2many_mod_pline('dm.campaign.purchase_line', 'campaign_id', "Items Purchase Lines",
                                                        domain=[('product_category','=','Items')], context={'product_category':'Items'}),
        'forwarding_charge' : fields.float('Forwarding Charge', digits=(16,2)),
        'payment_method_ids' : fields.many2many('account.journal','campaign_payment_method_rel','campaign_id','journal_id','Payment Methods',domain=[('type','=','cash')]),
        'mail_service_ids': fields.one2many('dm.campaign.mail_service','campaign_id','Mailing Service'),        
    }

    _defaults = {
        'state': lambda *a: 'draft',
        'manufacturing_state': lambda *a: 'pending',
        'items_state': lambda *a: 'pending',
        'translation_state': lambda *a: 'pending',
        'customer_file_state': lambda *a: 'pending',
        'dtp_state': lambda *a: 'pending',
        'responsible_id' : lambda obj, cr, uid, context: uid,
    }

    def state_draft_set(self, cr, uid, ids, *args):
        self.write(cr, uid, ids, {'state':'draft'})
        return True

    def state_close_set(self, cr, uid, ids, *args):
        for camp in self.browse(cr,uid,ids):
            if (camp.date > time.strftime('%Y-%m-%d')):
                raise osv.except_osv("Error!!","Campaign cannot be closed before end date!!!")
        self.write(cr, uid, ids, {'state':'close'})
        return True

    def check_forbidden_country(self,cr, uid, offer_id,country):
        offers = self.pool.get('dm.offer').browse(cr, uid, offer_id)
        forbidden_state_ids = [state_id.country_id.id for state_id in offers.forbidden_state_ids]
        forbidden_country_ids = [country_id.id for country_id in offers.forbidden_country_ids]
        forbidden_country_ids.extend(forbidden_state_ids)
        if country  in  forbidden_country_ids :
            return False
        return True      

    def state_pending_set(self, cr, uid, ids, *args):
        self.manufacturing_state_inprogress_set(cr, uid, ids, *args)
        self.dtp_state_inprogress_set(cr, uid, ids, *args)
        self.customer_file_state_inprogress_set(cr, uid, ids, *args)
        self.items_state_inprogress_set(cr, uid, ids, *args)
        self.write(cr, uid, ids, {'state':'pending'})
        return True

    def state_open_set(self, cr, uid, ids, *args):
        camp = self.browse(cr,uid,ids)[0]
        if not camp.date_start or not camp.dealer_id or not camp.trademark_id or not camp.lang_id or not camp.currency_id:
            raise osv.except_osv("Error!!","Informations are missing. Check Drop Date, Dealer, Trademark, Language and Currency")

        if ((camp.manufacturing_state != 'done') or (camp.dtp_state != 'done') or (camp.customer_file_state != 'done') or (camp.items_state != 'done')):
            raise osv.except_osv(
                _('Could not open this Campaign !'),
                _('You must first close all states related to this campaign.'))

        if (camp.date_start > time.strftime('%Y-%m-%d')):
            raise osv.except_osv("Error!!","Campaign cannot be opened before drop date!!!")

        """ Create Flow Start Workitems """
        print "Starting Campaign"
        start_type_ids = self.pool.get('dm.offer.step.type').search(cr, uid, [('flow_start','=',True)])
        print "start_type_ids : ",start_type_ids
        step_ids = self.pool.get('dm.offer.step').search(cr, uid, [('offer_id','=',camp.offer_id.id),('type_id','in',start_type_ids)])
        print "step_ids : ",step_ids

        for step in step_ids:
            for propo in camp.proposition_ids:
                for seg in propo.segment_ids:
                    if seg.type_src == 'internal' and seg.customers_file_id:
                        res = self.pool.get('dm.workitem').create(cr, uid, {'segment_id':seg.id, 'step_id':step,
                            'source':seg.customers_file_id.source, 'action_time': time.strftime("%Y-%m-%d %H:%M:%S")})
                        print "created wi :",res

        self.write(cr, uid, ids, {'state':'open','planning_state':'inprogress'})

        ''' create offer history'''
        history_vals={
              'offer_id' : camp.offer_id.id,
              'date' : camp.date_start,
              'campaign_id' : camp.id,
              'code' : camp.code1,
              'responsible_id' : camp.responsible_id.id,
              }
        history=self.pool.get("dm.offer.history")
        history.create(cr, uid, history_vals,{})
        return True

    def manufacturing_state_inprogress_set(self, cr, uid, ids, *args):
        for id in self.browse(cr,uid,ids):
            if (id.state == 'draft') or (id.state == 'pending'):
                self.write(cr, uid, ids, {'manufacturing_state':'inprogress'})
            else:
                raise osv.except_osv("Error!!","You cannot be set back to 'In Progress' once the campaign is opened!!!")
        return True

    def dtp_state_inprogress_set(self, cr, uid, ids, *args):
        for id in self.browse(cr,uid,ids):
            if (id.state == 'draft') or (id.state == 'pending'):
                self.write(cr, uid, ids, {'dtp_state':'inprogress'})
            else:
                raise osv.except_osv("Error!!","You cannot be set back to 'In Progress' once the campaign is opened!!!")
        return True
 
    def customer_file_state_inprogress_set(self, cr, uid, ids, *args):
        for id in self.browse(cr,uid,ids):
            if (id.state == 'draft') or (id.state == 'pending'):
                self.write(cr, uid, ids, {'customer_file_state':'inprogress'})
            else:
                raise osv.except_osv("Error!!","You cannot be set back to 'In Progress' once the campaign is opened!!!")
        return True       
    
    def items_state_inprogress_set(self, cr, uid, ids, *args):
        for id in self.browse(cr,uid,ids):
            if (id.state == 'draft') or (id.state == 'pending'):
                self.write(cr, uid, ids, {'items_state':'inprogress'})
            else:
                raise osv.except_osv("Error!!","You cannot be set back to 'In Progress' once the campaign is opened!!!")
        return True 
    
    def manufacturing_state_done_set(self, cr, uid, ids, *args):
        self.write(cr, uid, ids, {'manufacturing_state':'done'})
        return True
    
    def dtp_state_done_set(self, cr, uid, ids, *args):
        self.write(cr, uid, ids, {'dtp_state':'done'})
        return True

    def customer_file_state_done_set(self, cr, uid, ids, *args):
        self.write(cr, uid, ids, {'customer_file_state':'done'})
        return True
    
    def items_state_done_set(self, cr, uid, ids, *args):
        self.write(cr, uid, ids, {'items_state':'done'})
        return True

    def write(self, cr, uid, ids, vals, context=None):
        camp = self.pool.get('dm.campaign').browse(cr,uid,ids)[0]
        if not self.check_forbidden_country(cr, uid, camp.offer_id.id,camp.country_id.id):
            raise osv.except_osv("Error!!","You cannot use this offer in this country")        

        # In campaign, if no forwarding_charge is given, it gets the 'forwarding_charge' from offer
#        if not camp.forwarding_charge:
#            if camp.country_id.forwarding_charge:
#                vals['forwarding_charge'] = camp.country_id.forwarding_charge
        
        if camp.country_id.payment_method_ids:
            payment_methods = [payment_methods.id for payment_methods in camp.country_id.payment_method_ids]
            vals['payment_method_ids'] = [[6,0,payment_methods]]
            
        # Set campaign end date at one year after start date if end date does not exist
        if 'date_start' in vals and vals['date_start']:
            time_format = "%Y-%m-%d"
            d = time.strptime(vals['date_start'],time_format)
            d = datetime.date(d[0], d[1], d[2])
            date_end = d + datetime.timedelta(days=365)
            vals['date'] = date_end
            if 'project_id' in vals and vals['project_id']:
                self.pool.get('project.project').write(cr,uid,[vals['project_id']],{'date_end':vals['date_start']})

        """ In campaign, if no trademark is given, it gets the 'recommended trademark' from offer """
        if (not camp.trademark_id) and camp.offer_id.recommended_trademark_id:
            vals['trademark_id'] = camp.offer_id.recommended_trademark_id.id

        if 'trademark_id' in vals and vals['trademark_id']:
            trademark_id = vals['trademark_id']
        else:
            trademark_id = camp.trademark_id.id
        if 'dealer_id' in vals and vals['dealer_id']:
            dealer_id = vals['dealer_id']
        else:
            dealer_id = camp.dealer_id.id
        if 'country_id' in vals and vals['country_id']:
            country_id = vals['country_id']
        else:
            country_id = camp.country_id.id
            
#        check if an overlay exists else create it
        overlay_country_ids=[] 
        if trademark_id and dealer_id and country_id:
            overlay_obj = self.pool.get('dm.overlay')
            overlay_id = overlay_obj.search(cr, uid, [('trademark_id','=',trademark_id), ('dealer_id','=',dealer_id)])
            if overlay_id :
                browse_overlay = overlay_obj.browse(cr, uid, overlay_id)[0]
                overlay_country_ids = [country_ids.id for country_ids in browse_overlay.country_ids]
                vals['overlay_id']=overlay_id[0]
                if not (country_id in overlay_country_ids):
                    overlay_country_ids.append(country_id)
                    overlay_obj.write(cr, uid, browse_overlay.id, {'country_ids':[[6,0,overlay_country_ids]]}, context)
            else:
                overlay_ids1 = overlay_obj.create(cr, uid, {'trademark_id':trademark_id, 'dealer_id':dealer_id, 'country_ids':[[6,0,[country_id]]]}, context)
                vals['overlay_id'] = overlay_ids1
        return super(dm_campaign,self).write(cr, uid, ids, vals, context)
    
    def create(self,cr,uid,vals,context={}):

        type_id = self.pool.get('dm.campaign.type').search(cr, uid, [('code','=','model')])[0]
        if context.has_key('campaign_type') and context['campaign_type']=='model':
            vals['campaign_type_id']=type_id
        id_camp = super(dm_campaign,self).create(cr,uid,vals,context)
        data_cam = self.browse(cr, uid, id_camp)
        if not self.check_forbidden_country(cr, uid, data_cam.offer_id.id,data_cam.country_id.id):
            raise osv.except_osv("Error!!","You cannot use this offer in this country")        
        ''' create campaign mail service '''

#        mail_service_id = for each step in the offer the system should :
#            - check the media of the step,
#            - find the default mail service for that media
#            - assign it to mail_service_id
#        action_id = the action_id of the mail service
        mail_service_obj = self.pool.get('dm.mail_service')
        for step_id in data_cam.offer_id.step_ids :
            mail_service_id = mail_service_obj.search(cr,uid,[('media_id','=',step_id.media_id.id),('default_for_media','=',True)])
            mail_service = mail_service_obj.browse(cr,uid,mail_service_id)
            for mail in mail_service:
                mail_vals = {
                             'campaign_id'      : id_camp,
                             'offer_step_id'    : step_id.id,
                             'mail_service_id'  : mail.id,
    #                         'action_id'        : mail_service.action_id.id
                             }
                self.pool.get('dm.campaign.mail_service').create(cr,uid,mail_vals)           
        # In campaign, if no forwarding_charge is given, it gets the 'forwarding_charge' from offer
        write_vals = {}
#        if not data_cam.forwarding_charge:
#            if data_cam.country_id.forwarding_charge:
#                write_vals['forwarding_charge'] = data_cam.country_id.forwarding_charge
                    
        if data_cam.country_id.payment_method_ids:
            payment_methods = [payment_methods.id for payment_methods in data_cam.country_id.payment_method_ids]
            write_vals['payment_method_ids']=[[6,0,payment_methods]]
            
        # Set campaign end date at one year after start date if end date does not exist
        if (data_cam.date_start) and (not data_cam.date):
            d = time.strptime(data_cam.date_start,"%Y-%m-%d")
            d = datetime.date(d[0], d[1], d[2])
            date_end = d + datetime.timedelta(days=365)
            write_vals['date']=date_end
                
        # Set trademark to offer's trademark only if trademark is null
        if vals['campaign_type_id'] != type_id:
            if vals['offer_id'] and (not vals['trademark_id']):
                offer_id = self.pool.get('dm.offer').browse(cr, uid, vals['offer_id'])
                write_vals['trademark_id'] = offer_id.recommended_trademark_id.id
        if write_vals :
            super(dm_campaign,self).write(cr, uid, id_camp, write_vals)

        # check if an overlay exists else create it
        data_cam1 = self.browse(cr, uid, id_camp)
        overlay_country_ids = []
        if data_cam1.trademark_id and data_cam1.dealer_id and data_cam1.country_id:
            overlay_obj = self.pool.get('dm.overlay')
            overlay_id = overlay_obj.search(cr, uid, [('trademark_id','=',data_cam1.trademark_id.id), ('dealer_id','=',data_cam1.dealer_id.id)])
            new_write_vals ={}
            if overlay_id :
                browse_overlay = overlay_obj.browse(cr, uid, overlay_id)[0]
                overlay_country_ids = [country_ids.id for country_ids in browse_overlay.country_ids]
                new_write_vals['overlay_id']=overlay_id[0]
                if not (data_cam1.country_id.id in overlay_country_ids):
                    overlay_country_ids.append(data_cam1.country_id.id)
                    overlay_obj.write(cr, uid, browse_overlay.id, {'country_ids':[[6,0,overlay_country_ids]]}, context)
            else:
                overlay_ids1 = overlay_obj.create(cr, uid, {'trademark_id':data_cam1.trademark_id.id, 'dealer_id':data_cam1.dealer_id.id, 'country_ids':[[6,0,[data_cam1.country_id.id]]]}, context)
                new_write_vals['overlay_id'] = overlay_ids1
            super(dm_campaign, self).write(cr, uid, data_cam1.id, new_write_vals, context)  
        return id_camp            

    def fields_view_get(self, cr, user, view_id=None, view_type='form', context=None, toolbar=False):
        result = super(dm_campaign,self).fields_view_get(cr, user, view_id, view_type, context, toolbar)
        if context.has_key('campaign_type'):
            if context['campaign_type'] == 'model' :
                if result.has_key('toolbar'):
                    result['toolbar']['action'] =[]
        return result

    def copy_campaign(self,cr, uid, ids, *args):
        camp = self.browse(cr,uid,ids)[0]
        default={}
        default['name']='New campaign from model %s' % camp.name
        default['campaign_type_id'] = self.pool.get('dm.campaign.type').search(cr, uid, [('code','=','recruiting')])[0]
        default['responsible_id'] = uid
        self.copy(cr,uid,ids[0],default)
        return True

    def copy(self, cr, uid, id, default=None, context={}):
        cmp_id = super(dm_campaign, self).copy(cr, uid, id, default, context=context)
        data = self.browse(cr, uid, cmp_id, context)
        if 'name' in default:
            name_default=default['name']
        else:
            name_default='Copy of %s' % data.name
        super(dm_campaign, self).write(cr, uid, cmp_id, {'name':name_default, 'date_start':0, 'date':0, 'project_id':0})
        return cmp_id

    def unlink(self, cr, uid, ids, context={}):
        for campaign in self.browse(cr, uid, ids, context):
            history_id = self.pool.get('dm.offer.history').search(cr, uid, [('campaign_id','=',campaign.id)])
            self.pool.get('dm.offer.history').unlink(cr, uid, history_id, context)
        return super(dm_campaign, self).unlink(cr, uid, ids, context)

dm_campaign()


class dm_campaign_proposition(osv.osv):
    _name = "dm.campaign.proposition"
    _inherits = {'account.analytic.account': 'analytic_account_id'}

    def default_get(self, cr, uid, fields, context=None):
        value = super(dm_campaign_proposition, self).default_get(cr, uid, fields, context)
        if 'camp_id' in context:
            campaign = self.pool.get('dm.campaign').browse(cr, uid, context['camp_id'])
            value['date_start'] = campaign.date_start
        return value

    def write(self, cr, uid, ids, vals, context=None):
        if 'camp_id' in vals and vals['camp_id']:
            campaign = self.pool.get('dm.campaign').browse(cr, uid, vals['camp_id'])
            if campaign.date_start:
                vals['date_start']=campaign.date_start
            else:
                vals['date_start'] = 0
        return super(dm_campaign_proposition,self).write(cr, uid, ids, vals, context)

    def create(self,cr,uid,vals,context={}):
        id = self.pool.get('dm.campaign').browse(cr, uid, vals['camp_id'])
        if 'date_start' in vals and not vals['date_start']:
            if id.date_start:
                vals['date_start']=id.date_start
        if 'forwarding_charge' not in vals:
            if id.country_id.forwarding_charge:
                vals['forwarding_charge']=id.country_id.forwarding_charge
        if id.payment_method_ids:
            payment_methods = [payment_methods.id for payment_methods in id.payment_method_ids]
            vals['payment_method_ids'] = [[6,0,payment_methods]]
        return super(dm_campaign_proposition, self).create(cr, uid, vals, context)
    
    def copy(self, cr, uid, id, default=None, context={}):
        """
        Function to duplicate segments only if 'keep_segments' is set to yes else not to duplicate segments
        """
        proposition_id = super(dm_campaign_proposition, self).copy(cr, uid, id, default, context=context)
        data = self.browse(cr, uid, proposition_id, context)
        default='Copy of %s' % data.name
        super(dm_campaign_proposition, self).write(cr, uid, proposition_id, {'name':default, 'date_start':0, 'initial_proposition_id':id})
        if data.keep_segments == False:
            l = []
            for i in data.segment_ids:
                 l.append(i.id)
                 self.pool.get('dm.campaign.proposition.segment').unlink(cr,uid,l)
                 super(dm_campaign_proposition, self).write(cr, uid, proposition_id, {'segment_ids':[(6,0,[])]})
        
        """
        Function to duplicate products only if 'keep_prices' is set to yes else not to duplicate products
        """
        if data.keep_prices == False:
            l = []
            for i in data.item_ids:
                 l.append(i.id)
                 self.pool.get('dm.campaign.proposition.item').unlink(cr,uid,l)
                 super(dm_campaign_proposition, self).write(cr, uid, proposition_id, {'item_ids':[(6,0,[])]})
        return proposition_id

    def _proposition_code(self, cr, uid, ids, name, args, context={}):
        result ={}
        for id in ids:
            pro = self.browse(cr,uid,[id])[0]
            pro_ids = self.search(cr,uid,[('camp_id','=',pro.camp_id.id)])
            i=1
            for pro_id in pro_ids:
                camp_code = pro.camp_id.code1 or ''
                offer_code = pro.camp_id.offer_id and pro.camp_id.offer_id.code or ''
                trademark_code = pro.camp_id.trademark_id and pro.camp_id.trademark_id.name or ''
                dealer_code =pro.camp_id.dealer_id and pro.camp_id.dealer_id.ref or ''
                date_start = pro.date_start or ''
                date = date_start.split('-')
                year = month = ''
                if len(date)==3:
                    year = date[0][2:]
                    month = date[1]
                country_code = pro.camp_id.country_id.code or ''
                seq = '%%0%sd' % 2 % i
                final_date = month+year
                code1='-'.join([camp_code, seq])
                result[pro_id]=code1
                i +=1
        return result

    def _quantity_wanted_get(self, cr, uid, ids, name, args, context={}):
        result ={}
        for propo in self.browse(cr,uid,ids):
            if not propo.segment_ids:
                result[propo.id]='No segments defined'
                continue
            qty = 0
            numeric=True
            for segment in propo.segment_ids:
                if segment.all_add_avail:
                    result[propo.id]='AAA for a Segment'
                    numeric=False
                    continue
                if not segment.quantity_wanted:
                    result[propo.id]='Wanted Quantity missing in a Segment'
                    numeric=False
                    continue
                qty += segment.quantity_wanted
            if numeric:
                result[propo.id]=str(qty)
        return result

    def _quantity_planned_get(self, cr, uid, ids, name, args, context={}):
        result ={}
        for propo in self.browse(cr,uid,ids):
            if not propo.segment_ids:
                result[propo.id]='No segments defined'
                continue
            qty = 0
            for segment in propo.segment_ids:
                if segment.quantity_planned == 0:
                    result[propo.id]='planned Quantity missing in a Segment'
                    continue
                qty += segment.quantity_planned
            result[propo.id]=str(qty)
        return result

    def _quantity_delivered_get(self, cr, uid, ids, name, args, context={}):
        result ={}
        for propo in self.browse(cr,uid,ids):
            if not propo.segment_ids:
                result[propo.id]='No segments defined'
                continue
            qty = 0
            for segment in propo.segment_ids:
                if segment.quantity_delivered == 0:
                    result[propo.id]='Delivered Quantity missing in a Segment'
                    continue
                qty += segment.quantity_delivered
            result[propo.id]=str(qty)
        return result

    def _quantity_usable_get(self, cr, uid, ids, name, args, context={}):
        result={}
        for propo in self.browse(cr,uid,ids):
            if not propo.segment_ids:
                result[propo.id]='No segments defined'
                continue
            qty = 0
            for segment in propo.segment_ids:
                if segment.quantity_usable == 0:
                    result[propo.id]='Usable Quantity missing in a Segment'
                    continue
                qty += segment.quantity_usable
            result[propo.id]=str(qty)
        return result

    def _quantity_real_get(self, cr, uid, ids, name, args, context={}):
        result={}
        for propo in self.browse(cr,uid,ids):
            if not propo.segment_ids:
                result[propo.id]='No segments defined'
                continue
            qty = 0
            for segment in propo.segment_ids:
                if segment.quantity_real == 0:
                    result[propo.id]='Real Quantity missing in a Segment'
                    continue
                qty += segment.quantity_real
            result[propo.id]=str(qty)
        return result

    def _default_camp_date(self, cr, uid, context={}):
        if 'date1' in context and context['date1']:
            dd = context['date1']
            return dd
        return []

    _columns = {
        'code1' : fields.function(_proposition_code,string='Code',type="char",size=64,method=True,readonly=True),
        'camp_id' : fields.many2one('dm.campaign','Campaign',ondelete = 'cascade',required=True),
        'sale_rate' : fields.float('Sale Rate (%)', digits=(16,2),
                    help='This is the planned sale rate (in percent) for this commercial proposition'),
        'proposition_type' : fields.selection([('init','Initial'),('relaunching','Relauching'),('split','Split')],"Type"),
        'initial_proposition_id': fields.many2one('dm.campaign.proposition', 'Initial proposition'),
        'segment_ids' : fields.one2many('dm.campaign.proposition.segment','proposition_id','Segment', ondelete='cascade'),
        'quantity_planned' : fields.integer('Planned Quantity', help='The planned quantity is an estimation of the usable quantity of addresses you  will get after delivery, deduplication and cleaning\n' \
                            'This is usually the quantity used to order the manufacturing of the mailings'),
        'quantity_wanted' : fields.function(_quantity_wanted_get,string='Wanted Quantity',type="char",size=64,method=True,readonly=True,
                    help='The wanted quantity is the number of addresses you wish to get for that segment.\n' \
                            'This is usually the quantity used to order Customers Lists\n' \
                            'The wanted quantity could be AAA for All Addresses Available'),
        'quantity_delivered' : fields.function(_quantity_delivered_get,string='Delivered Quantity',type="char",size=64,method=True,readonly=True,
                    help='The delivered quantity is the number of addresses you receive from the broker.'),
        'quantity_usable' : fields.function(_quantity_usable_get,string='Usable Quantity',type="char",size=64,method=True,readonly=True,
                    help='The usable quantity is the number of addresses you have after delivery, deduplication and cleaning.'),
        'quantity_real' : fields.function(_quantity_real_get,string='Real Quantity',type="char",size=64,method=True,readonly=True,
                    help='The real quantity is the number of addresses you really get in the file.'),
        'starting_mail_price' : fields.float('Starting Mail Price',digits=(16,2)),
        'customer_pricelist_id':fields.many2one('product.pricelist','Product Pricelist', required=False),
        'forwarding_charges' : fields.float('Forwarding Charges', digits=(16,2)),
        'notes':fields.text('Notes'),
        'analytic_account_id' : fields.many2one('account.analytic.account','Analytic Account', ondelete='cascade'),
        'item_ids' : fields.one2many('dm.campaign.proposition.item', 'proposition_id', 'Catalogue'),
        'payment_method_ids' : fields.many2many('account.journal','proposition_payment_method_rel','proposition_id','journal_id','Payment Methods',domain=[('type','=','cash')]),
        'keep_segments' : fields.boolean('Keep Segments'),
        'keep_prices' : fields.boolean('Keep Prices At Duplication'),
        'force_sm_price' : fields.boolean('Force Starting Mail Price'),
        'price_prog_use' : fields.boolean('Price Progression'),
        'sm_price' : fields.float('Starting Mail Price', digits=(16,2)),
#        'prices_prog_id' : fields.many2one('dm.campaign.proposition.prices_progression', 'Prices Progression'),
        'manufacturing_costs': fields.float('Manufacturing Costs',digits=(16,2)),
        'forwarding_charge' : fields.float('Forwarding Charge', digits=(16,2)),
    }

    _defaults = {
        'proposition_type' : lambda *a : 'init',
#        'date_start' : _default_camp_date,
        'keep_segments' : lambda *a : True,
        'keep_prices' : lambda *a : True
    }

    def _check(self, cr, uid, ids=False, context={}):
        '''
        Function called by the scheduler to create workitem from the segments of propositions.
        '''
        ids = self.search(cr,uid,[('date_start','=',time.strftime('%Y-%m-%d %H:%M:%S'))])
        for id in ids:
            res = self.browse(cr,uid,[id])[0]
            offer_step_id = self.pool.get('dm.offer.step').search(cr,uid,[('offer_id','=',res.camp_id.offer_id.id),('flow_start','=',True)])
            if offer_step_id :
                for segment in res.segment_ids:
                    vals = {'step_id':offer_step_id[0],'segment_id':segment.id}
                    new_id = self.pool.get('dm.offer.step.workitem').create(cr,uid,vals)
        return True

dm_campaign_proposition()


class dm_customers_list_recruit_origin(osv.osv):
    _name = "dm.customers_list.recruit_origin"
    _description = "The origin of the adresses of a list"
    _columns = {
        'name' : fields.char('Name', size=64, required=True),
        'code' : fields.char('Code', size=16, required=True),
    }
dm_customers_list_recruit_origin()

class dm_customers_list_type(osv.osv):
    _name = "dm.customers_list.type"
    _description = "Type of the adress list"
    _columns = {
        'name' : fields.char('Name', size=64, required=True),
        'code' : fields.char('Code', size=16, required=True),
    }
dm_customers_list_type()

class dm_customers_list(osv.osv):
    _name = "dm.customers_list"
    _description = "A list of addresses proposed by an adresses broker"
    _columns = {
        'name' : fields.char('Name', size=64, required=True),
        'code' : fields.char('Code', size=16, required=True),
        'owner_id' : fields.many2one('res.partner', 'Owner',domain=[('category_id','ilike','Owner')], context={'category':'Owner'}),
        'broker_id' : fields.many2one('res.partner', 'Broker', domain=[('category_id','ilike','Broker')], context={'category':'Broker'}),
        'country_id' : fields.many2one('res.country','Country'),
        'currency_id' : fields.many2one('res.currency','Currency'),
        'product_id' : fields.many2one('product.product','Product', domain=[('categ_id','ilike','Customers List')],
                                context={'category':'Customers List'}, required=True),
        'per_thousand_price' : fields.float('Price per Thousand',digits=(16,2)),
        'delivery_cost' : fields.float('Delivery Cost',digits=(16,2)),
        'selection_cost' : fields.float('Selection Cost Per Thousand',digits=(16,2)),
        'broker_cost' : fields.float('Broker Cost',digits=(16,2),
                    help='The amount given to the broker for the list renting'),
        'broker_discount' : fields.float('Broker Discount (%)',digits=(16,2)),
        'other_cost' : fields.float('Other Cost',digits=(16,2)),
        'invoice_base' : fields.selection([('net','Net Addresses Quantity'),('raw','Raw Addresses Quantity')],'Invoicing based on',
                    help='Net or raw quantity on which is based the final invoice depending of the term negociated with the broker.\n' \
                            'Net : Usable quantity after deduplication\n' \
                            'Raw : Delivered quantity\n' \
                            'Real : Realy used qunatity'),
        'recruiting_origin_id' : fields.many2one('dm.customers_list.recruit_origin','Recruiting Origin',
                    help='Origin of the recruiting of the adresses'),
        'list_type_id' : fields.many2one('dm.customers_list.type','Type'),
        'update_frq' : fields.integer('Update Frequency'),
        'notes': fields.text('Description'),
        'media_id' : fields.many2one('dm.media','Media'),
    }
    _defaults =  {
        'invoice_base': lambda *a: 'net',
    }
dm_customers_list()

#class dm_customers_file_source(osv.osv):
#    _name = "dm.customers_file.source"
#    _description = "Customer File Source"
#    _columns = {
#            'name' : fields.char('Name', size=64 ,required=True),
#            'code' : fields.char('code', size=64 ,required=True),
#            'desc' : fields.text('Description'),
#            }
#dm_customers_file_source()


class dm_customers_file(osv.osv):
    _name = "dm.customers_file"
    _description = "A File of addresses"

    _FILE_SOURCES = [
        ('address_id','Partner Addresses'),
    ]

    _columns = {
        'name' : fields.char('Name', size=64, required=True),
        'code' : fields.char('Code', size=16, required=True),
        'customers_list_id' : fields.many2one('dm.customers_list', 'Customers List'),
        'delivery_date' : fields.date('Delivery Date'),
        'address_ids' : fields.many2many('res.partner.address','dm_cust_file_address_rel','cust_file_id','address_id','Customers File Addresses'),
        'segment_ids' : fields.one2many('dm.campaign.proposition.segment', 'customers_file_id', 'Segments', readonly=True),
#        'source_id' :fields.many2one('dm.customers_file.source', 'Customers File Source'),
        'source' : fields.selection(_FILE_SOURCES, 'Source', required=True),
        'note' : fields.text('Notes'),
    }
    _defaults =  {
        'source': lambda *a: 'address_id',
    }

dm_customers_file()

class dm_campaign_proposition_segment(osv.osv):

    _name = "dm.campaign.proposition.segment"
    _inherits = {'account.analytic.account': 'analytic_account_id'}
    _description = "A subset of addresses coming from a customers file"

    def search(self, cr, uid, args, offset=0, limit=None, order=None, context=None, count=False):
        if context and 'dm_camp_id' in context:
            if not context['dm_camp_id']:
                return []
            res  = self.pool.get('dm.campaign').browse(cr, uid,context['dm_camp_id'])
            seg_ids = []
            for pro  in res.proposition_ids:
                seg_ids.extend(map(lambda x : x.id, pro.segment_ids))
            return seg_ids
        return super(dm_campaign_proposition_segment, self).search(cr, uid, args, offset, limit, order, context, count)

    def _quantity_usable_get(self, cr, uid, ids, name, args, context={}):
        result ={}
        for segment in self.browse(cr,uid,ids):
            result[segment.id]=segment.quantity_delivered - segment.quantity_dedup_dedup - segment.quantity_cleaned_dedup - segment.quantity_dedup_cleaner- segment.quantity_cleaned_cleaner
        return result

    def _quantity_purged_get(self, cr, uid, ids, name, args, context={}):
        result ={}
        for segment in self.browse(cr,uid,ids):
            result[segment.id]=segment.quantity_delivered - segment.quantity_usable
        return result

    def _segment_code(self, cr, uid, ids, name, args, context={}):
        result ={}
        for id in ids:
            seg = self.browse(cr,uid,[id])[0]
            if seg.customers_list_id:
                segment_list = self.search(cr,uid,[('customers_list_id','=',seg.customers_list_id.id)])
                i = 1 
                for s in segment_list:
                    country_code = seg.customers_list_id.country_id.code or ''
                    cust_list_code =  seg.customers_list_id.code
                    seq = '%%0%sd' % 2 % i
                    code1='-'.join([country_code[:3], cust_list_code[:3], seq[:4]])
                    result[s]=code1
                    i +=1
            elif seg.customers_file_id:
                segment_list = self.search(cr,uid,[('customers_file_id','=',seg.customers_file_id.id)])
                i = 1 
                for s in segment_list:
                    cust_file_code =  seg.customers_file_id.code
                    seq = '%%0%sd' % 2 % i
                    code1='-'.join([cust_file_code[:3], seq[:4]])
                    result[s]=code1
                    i +=1
            else :
                result[seg.id]=seg.type_src+'%d'%id
        return result

    def onchange_list(self, cr, uid, ids, customers_list, start_census, end_census):
        if customers_list:
            list = self.pool.get('dm.customers_list').browse(cr, uid, [customers_list])[0]
            if start_census == 0 and end_census == 0:
                file_name = list.name
            else:
                file_name = list.name + '-' + str(start_census) + '/' + str(end_census)
            return {'value':{'name':file_name}}
        return False

    _columns = {
        'code1' : fields.function(_segment_code, string='Code', type="char", size=64, method=True, readonly=True),
        'proposition_id' : fields.many2one('dm.campaign.proposition','Proposition', ondelete='cascade'),
        'type_src' : fields.selection([('internal','Internal'),('external','External')], 'Type'),
        'customers_list_id': fields.many2one('dm.customers_list','Customers List'),
        'customers_file_id': fields.many2one('dm.customers_file','Customers File'),
        'quantity_real' : fields.integer('Real Quantity',
                    help='The real quantity is the number of addresses that are really in the customers file (by counting).'),
        'quantity_planned' : fields.integer('planned Quantity',
                    help='The planned quantity is an estimation of the usable quantity of addresses you  will get after delivery, deduplication and cleaning\n' \
                            'This is usually the quantity used to order the manufacturing of the mailings'),
        'quantity_wanted' : fields.integer('Wanted Quantity',
                    help='The wanted quantity is the number of addresses you wish to get for that segment.\n' \
                            'This is usually the quantity used to order Customers Lists\n' \
                            'The wanted quantity could be AAA for All Addresses Available'),
        'quantity_delivered' : fields.integer('Delivered Quantity',
                    help='The delivered quantity is the number of addresses you receive from the broker.'),
        'quantity_dedup_dedup' : fields.integer('Deduplication Quantity',
                    help='The quantity of duplicated addresses removed by the deduplicator.'),
        'quantity_dedup_cleaner' : fields.integer('Deduplication Quantity',
                    help='The quantity of duplicated addresses removed by the cleaner.'),
        'quantity_cleaned_dedup' : fields.integer('Cleaned Quantity',
                    help='The quantity of wrong addresses removed by the deduplicator.'),
        'quantity_cleaned_cleaner' : fields.integer('Cleaned Quantity',
                    help='The quantity of wrong addresses removed by the cleaner.'),
        'quantity_usable' : fields.function(_quantity_usable_get,string='Usable Quantity',type="integer",method=True,readonly=True,
                    help='The usable quantity is the number of addresses you have after delivery, deduplication and cleaning.'),
        'quantity_purged' : fields.function(_quantity_purged_get,string='Purged Quantity',type="integer",method=True,readonly=True,
                    help='The purged quantity is the number of addresses removed from deduplication and cleaning.'),
        'all_add_avail': fields.boolean('All Adresses Available',
                    help='Used to order all adresses available in the customers list based on the segmentation criteria'),
        'split_id' : fields.many2one('dm.campaign.proposition.segment','Split'),
        'start_census' :fields.integer('Start Census',help='The recency is the time since the latest purchase.\n' \
                                    'For example : A 0-30 recency means all the customers that have purchased in the last 30 days'),
        'end_census' : fields.integer('End Census'),
        'deduplication_level' : fields.integer('Deduplication Level',
                    help='The deduplication level defines the order in which the deduplication takes place.'),
        'active' : fields.boolean('Active'),
        'reuse_id' : fields.many2one('dm.campaign.proposition.segment','Reuse'),
        'analytic_account_id' : fields.many2one('account.analytic.account','Analytic Account', ondelete='cascade'),
        'note' : fields.text('Notes'),
        'segmentation_criteria': fields.text('Segmentation Criteria'),
        'type_census' : fields.selection([('minutes', 'Minutes'),('hour','Hours'),('day','Days'),('month','Months')], 'Census Type'),
    }
    _order = 'deduplication_level'
    _defaults =  {
        'all_add_avail': lambda *a: True,
        'type_census': lambda *a: 'day',
        'type_src': lambda *a: 'internal',
    }

dm_campaign_proposition_segment()

AVAILABLE_ITEM_TYPES = [
    ('main','Main Item'),
    ('standart','Standart Item'),
]

class dm_campaign_proposition_item(osv.osv):
    _name = "dm.campaign.proposition.item"
    _rec_name = 'product_id'
    _columns = {
        'product_id' : fields.many2one('product.product', 'Product', required=True, context={'flag':True}),
        'qty_planned' : fields.integer('Planned Quantity'),
        'qty_real' : fields.integer('Real Quantity'),
        'price' : fields.float('Sale Price'),
        'proposition_id': fields.many2one('dm.campaign.proposition', 'Commercial Proposition'),
        'item_type': fields.selection(AVAILABLE_ITEM_TYPES, 'Product Type', size=64),
        'offer_step_type_id': fields.many2one('dm.offer.step.type','Offer Step Type'), 
        'notes' : fields.text('Notes'),
        'forecasted_yield' : fields.float('Forecasted Yield'),
    }
dm_campaign_proposition_item()


PURCHASE_LINE_TRIGGERS = [
    ('draft','At Draft'),
    ('open','At Open'),
    ('planned','At Planning'),
    ('close','At Close'),
    ('manual','Manual'),
]

PURCHASE_LINE_STATES = [
    ('pending','Pending'),
    ('requested','Quotations Requested'),
    ('ordered','Ordered'),
    ('delivered','Delivered'),
]

PURCHASE_LINE_TYPES = [
    ('manufacturing','Manufacturing'),
    ('items','Items'),
    ('customer_file','Customer Files'),
    ('translation','Translation'),
    ('dtp','DTP'),
]

QTY_TYPES = [
    ('quantity_planned','planned Quantity'),
    ('quantity_wanted','Wanted Quantity'),
    ('quantity_delivered','Delivered Quantity'),
    ('quantity_usable','Usable Quantity'),
]

DOC_TYPES = [
    ('po','Purchase Order'),
    ('rfq','Request For Quotation'),
]

class dm_campaign_purchase_line(osv.osv):
    _name = 'dm.campaign.purchase_line'
    _rec_name = 'product_id'

    def default_get(self, cr, uid, fields, context=None):
        if context.has_key('product_category'):
            raise osv.except_osv('Warning', "Purchase order generation is not yet implemented !!!")
        return super(dm_campaign_purchase_line, self).default_get(cr, uid, fields, context)

    def _get_uom_id(self, cr, uid, *args):
        cr.execute('select id from product_uom order by id limit 1')
        res = cr.fetchone()
        return res and res[0] or False

    def pline_doc_generate(self,cr, uid, ids, *args):
        """Genererates Documents (POs or Request fo Quotations) for Purchase Lines"""
        plines = self.browse(cr, uid ,ids)

        for pline in plines:
            if pline.state == 'pending':
                """if in a group, obj = 1st campaign of the group, if not it's the campaing"""
                if not (pline.campaign_group_id or pline.campaign_id):
                    raise  osv.except_osv('Warning', "There's no campaign or campaign group defined for this purchase line .")

                if pline.campaign_group_id:
                    if not pline.campaign_group_id.campaign_ids:
                        raise  osv.except_osv('Warning', "There's no campaign defined for the campaign group : %s" %(pline.campaign_group_id.name))
                    obj = pline.campaign_group_id.campaign_ids[0]
                    code = pline.campaign_group_id.code
                else:
                    obj = pline.campaign_id
                    code = pline.campaign_id.code1

                if not pline.product_id.seller_ids:
                    raise  osv.except_osv('Warning', "There's no supplier defined for this product : %s" % (pline.product_id.name,) )


                """If Mailing Manufacturing purchase line"""
                if int(pline.product_category) == self.pool.get('product.category').search(cr, uid,[('name','=','Mailing Manufacturing')])[0]:

                    """If the product is a compound product (BoM) => Add Subproducts infos in document notes"""
                    note = []
                    cr.execute("select id from mrp_bom where product_id = %s limit 1" % (pline.product_id.id))
                    bom_id = cr.fetchone()
                    if bom_id:
                        bom = self.pool.get('mrp.bom').browse(cr, uid, [bom_id[0]])[0]
                        note.append("Product Composed of : ")
                        note.append("---------------------------------------------------------------------------")
                        for bom_child in bom.child_ids:
                            note.append(bom_child.name)
                            note.append("---------------------------------------------------------------------------")

                    """Get Manufacturing Descriptions if asked"""
                    if pline.desc_from_offer:
                        for step in obj.offer_id.step_ids:
                            for const in step.manufacturing_constraint_ids:
                                if not const.country_ids:
                                    note.append("---------------------------------------------------------------------------")
                                    note.append("Description : ")
                                    note.append("---------------------------------------------------------------------------")
                                    note.append(const.name)
                                    note.append(const.constraint)
                                elif obj.country_id in const.country_ids:
                                    note.append("---------------------------------------------------------------------------")
                                    note.append(const.name + ' for country :' +  obj.country_id.name)
                                    note.append(const.constraint)

                    """Add note if defined"""
                    if pline.notes:
                        note.append("---------------------------------------------------------------------------")
                        note.append(pline.notes)
                    else:
                        note.append(' ')

                    """If Document Type is Request for Quotation => create 1 Request for Quotation/Supplier grouped in a Tender"""
                    """If Document Type is Purchase Order => Create One Purchase Order for the main Supplier"""
                    if pline.type_document == 'rfq':

                        """Create Purchase tender"""
                        tender_id = self.pool.get('purchase.tender').create(cr, uid,{'state':'open'})

                        """Get Suppliers infos"""
                        for supplier in pline.product_id.seller_ids:
                            partner_id = supplier.id
                            partner = supplier.name

                            address_id = self.pool.get('res.partner').address_get(cr, uid, [partner.id], ['default'])['default']
                            if not address_id:
                                raise osv.except_osv('Warning', "There's no default address defined for this partner : %s" % (partner.name,) )
                            delivery_address = address_id
                            pricelist_id = partner.property_product_pricelist_purchase.id
                            if not pricelist_id:
                                raise osv.except_osv('Warning', "There's no purchase pricelist defined for this partner : %s" % (partner.name,) )
                            price = self.pool.get('product.pricelist').price_get(cr, uid, [pricelist_id], pline.product_id.id, pline.quantity, False, {'uom': pline.uom_id.id})[pricelist_id]
                            newdate = DateTime.strptime(pline.date_planned, '%Y-%m-%d %H:%M:%S') - DateTime.RelativeDateTime(days=pline.product_id.product_tmpl_id.seller_delay or 0.0)

                            """Create Document"""
                            purchase_id = self.pool.get('purchase.order').create(cr, uid, {
                                'origin': code,
                                'partner_id': partner.id,
                                'partner_address_id': address_id,
                                #'dest_address_id': delivery_address.id,
                                'location_id': 1,
                                'pricelist_id': pricelist_id,
                                'notes': "\n".join(note),
                                'tender_id': tender_id,
                                'dm_campaign_purchase_line': pline.id
                            })

                            ''' Create po lines for each proposition (of each campaign if group)'''
                            lines = []
                            if pline.campaign_group_id:
                                for campaign in pline.campaign_group_id.campaign_ids:
                                    for propo in campaign.proposition_ids:
                                        line_name = propo.code1 + '-' + propo.type
                                        if pline.type_quantity == 'quantity_planned':
                                            if propo.quantity_planned.isdigit():
                                                quantity = propo.quantity_planned
                                            else : 
                                                raise osv.except_osv('Warning',
                                                    'Cannot get planned quantity, check prososition %s' % (propo.name,)) 
                                        elif pline.type_quantity == 'quantity_wanted':
                                            if propo.quantity_wanted.isdigit():
                                                quantity = propo.quantity_wanted
                                            elif propo.quantity_wanted == 'AAA for a Segment':
                                                raise osv.except_osv('Warning',
                                                    'Cannot use wanted quantity for Mailing Manufacturing if there is AAA defined for a segment')
                                            else :
                                                raise osv.except_osv('Warning',
                                                    'Cannot get wanted quantity, check prososition %s' % (propo.name,)) 
                                        elif pline.type_quantity == 'quantity_delivered':
                                            if propo.quantity_delivered.isdigit():
                                                quantity = propo.quantity_delivered
                                            else : 
                                                raise osv.except_osv('Warning',
                                                    'Cannot get delivered quantity, check prososition %s' % (propo.name,)) 
                                        elif pline.type_quantity == 'quantity_usable':
                                            if propo.quantity_usable.isdigit():
                                                quantity = propo.quantity_usable
                                            else : 
                                                raise osv.except_osv('Warning',
                                                    'Cannot get delivered quantity, check prososition %s' % (propo.name,)) 
                                        else:
                                            raise osv.except_osv('Warning','Error getting quantity for proposition %s' % (propo.name,))

                                        line = self.pool.get('purchase.order.line').create(cr, uid, {
                                           'order_id': purchase_id,
                                           'name': line_name,
                                           'product_qty': quantity,
                                           'product_id': pline.product_id.id,
                                           'product_uom': pline.uom_id.id,
                                           'price_unit': price,
                                           'date_planned': newdate.strftime('%Y-%m-%d %H:%M:%S'),
                                           'taxes_id': [(6, 0, [x.id for x in pline.product_id.product_tmpl_id.supplier_taxes_id])],
                                           'account_analytic_id': propo.analytic_account_id,
                                        })
                            else:
                                for propo in obj.proposition_ids:
                                    line_name = propo.code1 + '-' + propo.type

                                    if pline.type_quantity == 'quantity_planned':
                                        if propo.quantity_planned.isdigit():
                                            quantity = propo.quantity_planned
                                        else : 
                                            raise osv.except_osv('Warning',
                                                'Cannot get planned quantity, check prososition %s' % (propo.name,))
                                    elif pline.type_quantity == 'quantity_wanted':
                                        if propo.quantity_wanted.isdigit():
                                            quantity = propo.quantity_wanted
                                        elif propo.quantity_wanted == 'AAA for a Segment':
                                            raise osv.except_osv('Warning',
                                                'Cannot use wanted quantity for Mailing Manufacturing if there is AAA defined for a segment')
                                        else :
                                            raise osv.except_osv('Warning',
                                                'Cannot get wanted quantity, check prososition %s' % (propo.name,))
                                    elif pline.type_quantity == 'quantity_delivered':
                                        if propo.quantity_delivered.isdigit():
                                            quantity = propo.quantity_delivered
                                        else : 
                                            raise osv.except_osv('Warning',
                                                'Cannot get delivered quantity, check prososition %s' % (propo.name,))
                                    elif pline.type_quantity == 'quantity_usable':
                                        if propo.quantity_usable.isdigit():
                                            quantity = propo.quantity_usable
                                        else : 
                                            raise osv.except_osv('Warning',
                                                'Cannot get delivered quantity, check prososition %s' % (propo.name,))
                                    else:
                                        raise osv.except_osv('Warning','Error getting quantity for proposition %s' % (propo.name,))

                                    line = self.pool.get('purchase.order.line').create(cr, uid, {
                                       'order_id': purchase_id,
                                       'name': line_name,
                                       'product_qty': quantity,
                                       'product_id': pline.product_id.id,
                                       'product_uom': pline.uom_id.id,
                                       'price_unit': price,
                                       'date_planned': newdate.strftime('%Y-%m-%d %H:%M:%S'),
                                       'taxes_id': [(6, 0, [x.id for x in pline.product_id.product_tmpl_id.supplier_taxes_id])],
                                       'account_analytic_id': propo.analytic_account_id,
                                    })

                    elif pline.type_document == 'po':

                        """Create 1 PO for the main supplier"""
                        """Get the main supplier = the 1st product supplier with sequence = 1"""
                        cr.execute('select name from product_supplierinfo where product_id = %s and sequence = 1', (pline.product_id.id,))
                        res = cr.fetchone()
                        supplier = self.pool.get('res.partner').browse(cr,uid,[res[0]])[0]
                        partner_id = supplier.id
                        partner = supplier.name

                        address_id = self.pool.get('res.partner').address_get(cr, uid, [supplier.id], ['default'])['default']
                        if not address_id:
                            raise osv.except_osv('Warning', "There's no default address defined for this partner : %s" % (supplier.name,) )
                        delivery_address = address_id
                        pricelist_id = supplier.property_product_pricelist_purchase.id
                        if not pricelist_id:
                            raise osv.except_osv('Warning', "There's no purchase pricelist defined for this partner : %s" % (supplier.name,) )
                        price = self.pool.get('product.pricelist').price_get(cr, uid, [pricelist_id], pline.product_id.id, pline.quantity, False, {'uom': pline.uom_id.id})[pricelist_id]
                        newdate = DateTime.strptime(pline.date_planned, '%Y-%m-%d %H:%M:%S') - DateTime.RelativeDateTime(days=pline.product_id.product_tmpl_id.seller_delay or 0.0)

                        """Create Document"""
                        purchase_id = self.pool.get('purchase.order').create(cr, uid, {
                            'origin': code,
                            'partner_id': supplier.id,
                            'partner_address_id': address_id,
                            #'dest_address_id': delivery_address.id,
                            'location_id': 1,
                            'pricelist_id': pricelist_id,
                            'notes': "\n".join(note),
                            'dm_campaign_purchase_line': pline.id
                        })

                        # Set as PO
                        wf_service = netsvc.LocalService("workflow")
                        wf_service.trg_validate(uid, 'purchase.order', purchase_id, 'purchase_confirm', cr)

                        ''' Create po lines for each proposition (of each campaign if group)'''
                        lines = []
                        if pline.campaign_group_id:
                            for campaign in pline.campaign_group_id.campaign_ids:
                                for propo in campaign.proposition_ids:
                                    line_name = propo.code1 + '-' + propo.type
                                    if pline.type_quantity == 'quantity_planned':
                                        if propo.quantity_planned.isdigit():
                                            quantity = propo.quantity_planned
                                        else : 
                                            raise osv.except_osv('Warning',
                                                'Cannot get planned quantity, check prososition %s' % (propo.name,)) 
                                    elif pline.type_quantity == 'quantity_wanted':
                                        if propo.quantity_wanted.isdigit():
                                            quantity = propo.quantity_wanted
                                        elif propo.quantity_wanted == 'AAA for a Segment':
                                            raise osv.except_osv('Warning',
                                                'Cannot use wanted quantity for Mailing Manufacturing if there is AAA defined for a segment')
                                        else :
                                            raise osv.except_osv('Warning',
                                                'Cannot get wanted quantity, check prososition %s' % (propo.name,)) 
                                    elif pline.type_quantity == 'quantity_delivered':
                                        if propo.quantity_delivered.isdigit():
                                            quantity = propo.quantity_delivered
                                        else : 
                                            raise osv.except_osv('Warning',
                                                'Cannot get delivered quantity, check prososition %s' % (propo.name,)) 
                                    elif pline.type_quantity == 'quantity_usable':
                                        if propo.quantity_usable.isdigit():
                                            quantity = propo.quantity_usable
                                        else : 
                                            raise osv.except_osv('Warning',
                                                'Cannot get delivered quantity, check prososition %s' % (propo.name,)) 
                                    else:
                                        raise osv.except_osv('Warning','Error getting quantity for proposition %s' % (propo.name,))

                                    line = self.pool.get('purchase.order.line').create(cr, uid, {
                                       'order_id': purchase_id,
                                       'name': line_name,
                                       'product_qty': quantity,
                                       'product_id': pline.product_id.id,
                                       'product_uom': pline.uom_id.id,
                                       'price_unit': price,
                                       'date_planned': newdate.strftime('%Y-%m-%d %H:%M:%S'),
                                       'taxes_id': [(6, 0, [x.id for x in pline.product_id.product_tmpl_id.supplier_taxes_id])],
                                       'account_analytic_id': propo.analytic_account_id,
                                    })
                        else:
                            for propo in obj.proposition_ids:
                                line_name = propo.code1 + '-' + propo.type

                                if pline.type_quantity == 'quantity_planned':
                                    if propo.quantity_planned.isdigit():
                                        quantity = propo.quantity_planned
                                    else : 
                                        raise osv.except_osv('Warning',
                                            'Cannot get planned quantity, check prososition %s' % (propo.name,))
                                elif pline.type_quantity == 'quantity_wanted':
                                    if propo.quantity_wanted.isdigit():
                                        quantity = propo.quantity_wanted
                                    elif propo.quantity_wanted == 'AAA for a Segment':
                                        raise osv.except_osv('Warning',
                                            'Cannot use wanted quantity for Mailing Manufacturing if there is AAA defined for a segment')
                                    else :
                                        raise osv.except_osv('Warning',
                                            'Cannot get wanted quantity, check prososition %s' % (propo.name,))
                                elif pline.type_quantity == 'quantity_delivered':
                                    if propo.quantity_delivered.isdigit():
                                        quantity = propo.quantity_delivered
                                    else : 
                                        raise osv.except_osv('Warning',
                                            'Cannot get delivered quantity, check prososition %s' % (propo.name,))
                                elif pline.type_quantity == 'quantity_usable':
                                    if propo.quantity_usable.isdigit():
                                        quantity = propo.quantity_usable
                                    else : 
                                        raise osv.except_osv('Warning',
                                            'Cannot get delivered quantity, check prososition %s' % (propo.name,))
                                else:
                                    raise osv.except_osv('Warning','Error getting quantity for proposition %s' % (propo.name,))

                                line = self.pool.get('purchase.order.line').create(cr, uid, {
                                   'order_id': purchase_id,
                                   'name': line_name,
                                   'product_qty': quantity,
                                   'product_id': pline.product_id.id,
                                   'product_uom': pline.uom_id.id,
                                   'price_unit': price,
                                   'date_planned': newdate.strftime('%Y-%m-%d %H:%M:%S'),
                                   'taxes_id': [(6, 0, [x.id for x in pline.product_id.product_tmpl_id.supplier_taxes_id])],
                                   'account_analytic_id': propo.analytic_account_id,
                                })

                    else:
                        raise osv.except_osv('Warning', "The's no Document Type defined for this Purchase Line")

                    """If Customers List purchase line"""
                elif int(pline.product_category) == self.pool.get('product.category').search(cr, uid,[('name','=','Customers List')])[0]:

                    """Get Customers File note if asked"""
                    note = []
                    if pline.desc_from_offer:
                        note.append("---------------------------------------------------------------------------")
                        note.append('Campaign Name : %s' % (obj.name,))
                        note.append('Campaign Code : %s' % (obj.code1,))
                        note.append('Drop Date : %s' % (obj.date_start,))
                        note.append("---------------------------------------------------------------------------")
                        note.append('Trademark : %s' % (obj.trademark_id.name,))
                        note.append('planned Quantity : %s' % (obj.quantity_planned_total,))
                        note.append('Responsible : %s' % (obj.files_responsible_id.name,))

                    """Add note if defined"""
                    if pline.notes:
                        note.append("---------------------------------------------------------------------------")
                        note.append(pline.notes)
                    else:
                        note.append(' ')

                    """If Document Type is Request for Quotation => create 1 Request for Quotation/Supplier grouped in a Tender"""
                    """If Document Type is Purchase Order => Create One Purchase Order for the main Supplier"""
                    if pline.type_document == 'rfq':

                        """Create Purchase tender"""
                        tender_id = self.pool.get('purchase.tender').create(cr, uid,{'state':'open'})

                        """Get Suppliers infos"""
                        for supplier in pline.product_id.seller_ids:
                            partner_id = supplier.id
                            partner = supplier.name

                            address_id = self.pool.get('res.partner').address_get(cr, uid, [partner.id], ['default'])['default']
                            if not address_id:
                                raise osv.except_osv('Warning', "There's no default address defined for this partner : %s" % (partner.name,) )
                            delivery_address = address_id
                            pricelist_id = partner.property_product_pricelist_purchase.id
                            if not pricelist_id:
                                raise osv.except_osv('Warning', "There's no purchase pricelist defined for this partner : %s" % (partner.name,) )
                            price = self.pool.get('product.pricelist').price_get(cr, uid, [pricelist_id], pline.product_id.id, pline.quantity, False, {'uom': pline.uom_id.id})[pricelist_id]
                            newdate = DateTime.strptime(pline.date_planned, '%Y-%m-%d %H:%M:%S') - DateTime.RelativeDateTime(days=pline.product_id.product_tmpl_id.seller_delay or 0.0)

                            """Create Document"""
                            purchase_id = self.pool.get('purchase.order').create(cr, uid, {
                                'origin': code,
                                'partner_id': partner.id,
                                'partner_address_id': address_id,
                                #'dest_address_id': delivery_address.id,
                                'location_id': 1,
                                'pricelist_id': pricelist_id,
                                'notes': "\n".join(note),
                                'tender_id': tender_id,
                                'dm_campaign_purchase_line': pline.id
                            })

                            ''' Create po lines for each proposition (of each campaign if group)'''
                            lines = []
                            if pline.campaign_group_id:
                                for campaign in pline.campaign_group_id.campaign_ids:
                                    for propo in campaign.proposition_ids:
                                        for segment in propo.segment_ids:
                                            line_name = propo.code1 + ' - ' + segment.customers_file_id.name
                                            if pline.type_quantity == 'quantity_planned':
                                                quantity = segment.quantity_planned
                                            elif pline.type_quantity == 'quantity_wanted':
                                                quantity = segment.quantity_wanted
                                                if segment.all_add_Avail:
                                                    quantity = 0
                                                    line_name = propo.code1 + ' - ' + segment.customers_file_id.name + ' - All Addresses Available'
                                            elif pline.type_quantity == 'quantity_delivered':
                                                quantity = segment.quantity_delivered
                                            elif pline.type_quantity == 'quantity_usable':
                                                quantity = segment.quantity_usable
                                            else:
                                                raise osv.except_osv('Warning','Error getting quantity for proposition %s' % (propo.name,))

                                            line = self.pool.get('purchase.order.line').create(cr, uid, {
                                               'order_id': purchase_id,
                                               'name': line_name,
                                               'product_qty': quantity,
                                               'product_id': pline.product_id.id,
                                               'product_uom': pline.uom_id.id,
                                               'price_unit': price,
                                               'date_planned': newdate.strftime('%Y-%m-%d %H:%M:%S'),
                                               'taxes_id': [(6, 0, [x.id for x in pline.product_id.product_tmpl_id.supplier_taxes_id])],
                                               'account_analytic_id': propo.analytic_account_id,
                                            })
                            else:
                                for propo in obj.proposition_ids:
                                    for segment in propo.segment_ids:
                                        line_name = propo.code1 + ' - ' + segment.customers_list_id.name
                                        if pline.type_quantity == 'quantity_planned':
                                            quantity = segment.quantity_planned
                                        elif pline.type_quantity == 'quantity_wanted':
                                            quantity = segment.quantity_wanted
                                            if segment.all_add_avail:
                                                quantity = 0
                                                line_name = propo.code1 + ' - ' + segment.customers_list_id.name + ' - All Addresses Available'
                                        elif pline.type_quantity == 'quantity_delivered':
                                            quantity = propo.quantity_delivered
                                        elif pline.type_quantity == 'quantity_usable':
                                            quantity = propo.quantity_usable
                                        else:
                                            raise osv.except_osv('Warning','Error getting quantity for proposition %s' % (propo.name,))

                                        line = self.pool.get('purchase.order.line').create(cr, uid, {
                                           'order_id': purchase_id,
                                           'name': line_name,
                                           'product_qty': quantity,
                                           'product_id': pline.product_id.id,
                                           'product_uom': pline.uom_id.id,
                                           'price_unit': price,
                                           'date_planned': newdate.strftime('%Y-%m-%d %H:%M:%S'),
                                           'taxes_id': [(6, 0, [x.id for x in pline.product_id.product_tmpl_id.supplier_taxes_id])],
                                           'account_analytic_id': propo.analytic_account_id,
                                        })

                    elif pline.type_document == 'po':

                        """Create 1 PO for the main supplier"""
                        """Get the customers list = supplier in Customers List for that country"""

                        lists = []
                        for propo in obj.proposition_ids:
                            for segment in propo.segment_ids:
                                lists.append(segment.customers_list_id)
                        cust_lists = set(lists)

                        """Create 1 PO / Customets List"""
                        for list in cust_lists:
                            print "--- Enter List : ", list.name
                            partner = list.broker_id
                            address_id = self.pool.get('res.partner').address_get(cr, uid, [partner.id], ['default'])['default']
                            if not address_id:
                                raise osv.except_osv('Warning', "There's no default address defined for this partner : %s" % (partner.name,) )
                            if pline.campaign_id.cleaner_id :
                                dest_address_id = self.pool.get('res.partner').address_get(cr, uid, [pline.campaign_id.cleaner_id.id], ['default'])['default']
                                if not address_id:
                                    raise osv.except_osv('Warning', "There's no default address defined for this partner : %s" % (pline.campaign_id.cleaner_id.name,) )
                            elif pline.campaign_id.deduplicator_id :
                                dest_address_id = self.pool.get('res.partner').address_get(cr, uid, [pline.campaign_id.deduplicator_id.id], ['default'])['default']
                                if not address_id:
                                    raise osv.except_osv('Warning', "There's no default address defined for this partner : %s" % (pline.campaign_id.deduplicator_id.name,) )
                            elif pline.campaign_id.router_id :
                                dest_address_id = self.pool.get('res.partner').address_get(cr, uid, [pline.campaign_id.router_id.id], ['default'])['default']
                                if not address_id:
                                    raise osv.except_osv('Warning', "There's no default address defined for this partner : %s" % (pline.campaign_id.router_id.name,) )
                            else:
                                raise osv.except_osv('Warning', "There's no intermediaries defined for this campaign") 

                            pricelist_id = partner.property_product_pricelist_purchase.id
                            if not pricelist_id:
                                raise osv.except_osv('Warning', "There's no purchase pricelist defined for this partner : %s" % (partner.name,) )
                            newdate = DateTime.strptime(pline.date_planned, '%Y-%m-%d %H:%M:%S') - DateTime.RelativeDateTime(days=pline.product_id.product_tmpl_id.seller_delay or 0.0)

                            """Create Document"""
                            purchase_id = self.pool.get('purchase.order').create(cr, uid, {
                                'origin': code,
                                'partner_id': partner.id,
                                'partner_address_id': address_id,
                                'dest_address_id': dest_address_id,
                                'location_id': 1,
                                'pricelist_id': pricelist_id,
                                'notes': "\n".join(note),
                                'dm_campaign_purchase_line': pline.id
                            })

                            # Set as PO
                            wf_service = netsvc.LocalService("workflow")
                            wf_service.trg_validate(uid, 'purchase.order', purchase_id, 'purchase_confirm', cr)

                            """Creare a PO line / segment for that Customers List"""
                            lines = []
                            if pline.campaign_group_id:
                                for campaign in pline.campaign_group_id.campaign_ids:
                                    for propo in campaign.proposition_ids:
                                        for segment in propo.segment_ids:
                                            if segment.customers_list_id == list:
                                                line_name = propo.code1 + ' - ' + segment.customers_file_id.name
                                                if pline.type_quantity == 'quantity_planned':
                                                    quantity = segment.quantity_planned
                                                elif pline.type_quantity == 'quantity_wanted':
                                                    quantity = segment.quantity_wanted
                                                    if segment.all_add_Avail:
                                                        quantity = 0
                                                        line_name = propo.code1 + ' - ' + segment.customers_file_id.name + ' - All Addresses Available'
                                                elif pline.type_quantity == 'quantity_delivered':
                                                    quantity = segment.quantity_delivered
                                                elif pline.type_quantity == 'quantity_usable':
                                                    quantity = segment.quantity_usable
                                                else:
                                                    raise osv.except_osv('Warning','Error getting quantity for proposition %s' % (propo.name,))

                                                """Compute price"""
                                                price = ((list.per_thousand_price / 1000) * ((100 - list.broker_discount) / 100) * (list.selection_cost / 1000)) + list.delivery_cost + list.other_cost
                                                line = self.pool.get('purchase.order.line').create(cr, uid, {
                                                   'order_id': purchase_id,
                                                   'name': line_name,
                                                   'product_qty': quantity,
                                                   'product_id': pline.product_id.id,
                                                   'product_uom': pline.uom_id.id,
                                                   'price_unit': price,
                                                   'date_planned': newdate.strftime('%Y-%m-%d %H:%M:%S'),
                                                   'taxes_id': [(6, 0, [x.id for x in pline.product_id.product_tmpl_id.supplier_taxes_id])],
                                                   'account_analytic_id': propo.analytic_account_id,
                                                })
                            else:
                                for propo in obj.proposition_ids:
                                    for segment in propo.segment_ids:
                                        if segment.customers_list_id == list:
                                            line_name = propo.code1 + ' - ' + segment.customers_list_id.name
                                            if pline.type_quantity == 'quantity_planned':
                                                quantity = segment.quantity_planned
                                            elif pline.type_quantity == 'quantity_wanted':
                                                quantity = segment.quantity_wanted
                                                if segment.all_add_avail:
                                                    quantity = 0
                                                    line_name = propo.code1 + ' - ' + segment.customers_list_id.name + ' - All Addresses Available'
                                            elif pline.type_quantity == 'quantity_delivered':
                                                quantity = propo.quantity_delivered
                                            elif pline.type_quantity == 'quantity_usable':
                                                quantity = propo.quantity_usable
                                            else:
                                                raise osv.except_osv('Warning','Error getting quantity for proposition %s' % (propo.name,))

                                            """Compute price"""
                                            price = ((list.per_thousand_price / 1000) * ((100 - list.broker_discount) / 100) * (list.selection_cost / 1000)) + list.delivery_cost + list.other_cost
                                            line = self.pool.get('purchase.order.line').create(cr, uid, {
                                               'order_id': purchase_id,
                                               'name': line_name,
                                               'product_qty': quantity,
                                               'product_id': pline.product_id.id,
                                               'product_uom': pline.uom_id.id,
                                               'price_unit': price,
                                               'date_planned': newdate.strftime('%Y-%m-%d %H:%M:%S'),
                                               'taxes_id': [(6, 0, [x.id for x in pline.product_id.product_tmpl_id.supplier_taxes_id])],
                                               'account_analytic_id': propo.analytic_account_id,
                                            })

                    else:
                        raise osv.except_osv('Warning', "The's no Document Type defined for this Purchase Line")

                elif int(pline.product_category) == self.pool.get('product.category').search(cr, uid,[('name','=','DTP')])[0]:
                    """If DTP purchase line"""
                    raise osv.except_osv('Warning', "Purchase of DTP is not yet implemented")

                elif int(pline.product_category) == self.pool.get('product.category').search(cr, uid,[('name','=','Item')])[0]:
                    """If Items purchase line"""
                    raise osv.except_osv('Warning', "Purchase of items is not yet implemented")

                elif int(pline.product_category) == self.pool.get('product.category').search(cr, uid,[('name','=','Translation')])[0]:
                    """If Translation purchase line"""
                    raise osv.except_osv('Warning', "Purchase of translations is not yet implemented")

                    if not obj.lang_id:
                        raise osv.except_osv('Warning', "There's no language defined for this campaign : %s" % (obj.name,) )
                    if pline.notes:
                        constraints.append(pline.notes)
                    else:
                        constraints.append(' ')

                    quantity=0
                    for step in pline.campaign_id.offer_id.step_ids:
                        quantity += step.doc_number
                    line = self.pool.get('purchase.order.line').create(cr, uid, {
                       'order_id': purchase_id,
                       'name': code,
                       'product_qty': quantity,
                       'product_id': pline.product_id.id,
                       'product_uom': pline.uom_id.id,
                       'price_unit': price,
                       'date_planned': newdate.strftime('%Y-%m-%d %H:%M:%S'),
                       'taxes_id': [(6, 0, [x.id for x in pline.product_id.product_tmpl_id.supplier_taxes_id])],
#                           'account_analytic_id': obj.analytic_account_id,
                    })

                else:
                    raise osv.except_osv('Warning', "The's no Product Category defined for this Purchase Line")
        self.write(cr, uid, ids, {'state':'ordered'})
        return True

    def _default_date(self, cr, uid, context={}):
        if 'date1' in context and context['date1']:
            dd = context['date1']
            newdate =  DateTime.strptime(dd + ' 09:00:00','%Y-%m-%d %H:%M:%S')
            #print "From _default_date : ",newdate.strftime('%Y-%m-%d %H:%M:%S')
            return newdate.strftime('%Y-%m-%d %H:%M:%S')
        return []

    def _state_get(self, cr, uid, ids, name, args, context={}):
        result = {}
        for pline in self.browse(cr, uid, ids):
            delivered=False
            ordered=False
            print 'pline po ids : ',pline.purchase_order_ids
            if pline.purchase_order_ids:
                for po in pline.purchase_order_ids:
                    if delivered:
                        continue
                    if po.shipped:
                        result[pline.id]='delivered'
                        delivered=True
                        if pline.type == 'translation':
                            trans_id = self.pool.get('dm.offer.translation').create(cr, uid,
                                {'offer_id': pline.campaign_id.offer_id.id,
                                 'date': pline.date_delivery,
                                 'language_id': pline.campaign_id.lang_id.id,
                                 'translator_id':  po.partner_id.id,
                                 'notes': pline.notes,
                                 })
                        continue
                    if ordered:
                        continue
                    if po.state == 'confirmed' or po.state == 'approved':
                        result[pline.id]='ordered'
                        ordered=True
                    if po.state == 'draft':
                        result[pline.id]='requested'
            else:
                result[pline.id] = 'pending'
        return result

    def _delivery_date_get(self, cr, uid, ids, name, args, context={}):
        result = {}
        for pline in self.browse(cr, uid, ids):
            result[pline.id] = False
            for po in pline.purchase_order_ids:
                if po.shipped:
                    if po.picking_ids:
                        result[pline.id] = po.picking_ids[0].date_done
                    continue
        return result

    def _default_category_get(self, cr, uid, context):
        if 'product_category' in context and context['product_category']:
            cr.execute('select id from product_category where name=%s order by id limit 1', (context['product_category'],))
        else:
            cr.execute('select id from product_category where name=%s order by id limit 1', ('Mailing Manufacturing',))
        res = cr.fetchone()
        return str(res[0]) or False

    def _product_category_get(self,cr,uid,context={}):
        type_obj = self.pool.get('product.category')
        dmcat_id = type_obj.search(cr,uid,[('name','ilike','Direct Marketing')])[0]
        type_ids = type_obj.search(cr,uid,[('parent_id','=',dmcat_id)])
        type = type_obj.browse(cr,uid,type_ids)
        return map(lambda x : [str(x.id),x.name],type) 

    def _default_quantity_get(self, cr, uid, context):
        if 'product_category' in context and context['product_category']:
            if context['product_category'] == 'Mailing Manufacturing':
                return 'quantity_planned'
            elif context['product_category'] == 'Customers List':
                return 'quantity_wanted'
        return 'quantity_planned'

    def _default_doctype_get(self, cr, uid, context):
        if 'product_category' in context and context['product_category']:
            if context['product_category'] == 'Mailing Manufacturing':
                return 'rfq'
            elif context['product_category'] == 'Customers List':
                return 'po'
        return 'rfq'


    _columns = {
        'campaign_id': fields.many2one('dm.campaign', 'Campaign'),
        'campaign_group_id': fields.many2one('dm.campaign.group', 'Campaign Group'),
        'product_id' : fields.many2one('product.product', 'Product', required=True, context={'flag':True}),
        'quantity' : fields.integer('Total Quantity', readonly=False, required=True),
        'quantity_warning' : fields.char('Warning', size=128, readonly=True),
        'type_quantity' : fields.selection(QTY_TYPES, 'Quantity Type', size=32),
        'type_document' : fields.selection(DOC_TYPES, 'Document Type', size=32),
        'product_category' : fields.selection(_product_category_get, 'Product Category', size=64 ,select=True),
        'uom_id' : fields.many2one('product.uom','UOM', required=True),
        'date_order': fields.datetime('Order date', readonly=True),
        'date_planned': fields.datetime('Scheduled date', required=True),
        'date_delivery': fields.function(_delivery_date_get, method=True, type='datetime', string='Delivery Date', readonly=True),
        'trigger' : fields.selection(PURCHASE_LINE_TRIGGERS, 'Trigger'),
        'type' : fields.selection(PURCHASE_LINE_TYPES, 'Type'),
        'purchase_order_ids' : fields.one2many('purchase.order','dm_campaign_purchase_line','Campaign Purchase Line'),
        'notes': fields.text('Notes'),
        'togroup': fields.boolean('Apply to Campaign Group'),
        'desc_from_offer' : fields.boolean('Insert Description from Offer'),
        'state' : fields.function(_state_get, method=True, type='selection', selection=[
            ('pending','Pending'),
            ('requested','Quotations Requested'),
            ('ordered','Ordered'),
            ('delivered','Delivered'),
            ], string='State', store=True, readonly=True),
    }

    _defaults = {
#        'date_planned' : _default_date,
        'quantity' : lambda *a : 0,
        'product_category' : _default_category_get,
        'uom_id' : _get_uom_id,
        'trigger': lambda *a : 'manual',
        'state': lambda *a : 'pending',
        'type_quantity': _default_quantity_get,
        'type_document': _default_doctype_get,
        'desc_from_offer': lambda *a : True,
    }
dm_campaign_purchase_line()

class dm_campaign_manufacturing_cost(osv.osv):
    _name = 'dm.campaign.manufacturing_cost'
    _columns = {
        'name' : fields.char('Description', size=64, required=True),
        'amount': fields.float('Amount', digits=(16,2)),
        'campaign_id' : fields.many2one('dm.campaign','Campaign'),
    }
dm_campaign_manufacturing_cost()

class dm_campaign_proposition_prices_progression(osv.osv):
    _name = 'dm.campaign.proposition.prices_progression'
    _columns = {
        'name' : fields.char('Name', size=64, required=True),
        'fixed_prog' : fields.float('Fixed Prices Progression', digits=(16,2)),
        'percent_prog' : fields.float('Percentage Prices Progression', digits=(16,2)),
    }
dm_campaign_proposition_prices_progression()

class dm_campaign_document_type(osv.osv):
    _name = 'dm.campaign.document.type'
    _columns = {
        'name' : fields.char('Name', size=64, required=True),
        'code' : fields.char('Code', size=64, required=True),
    }
dm_campaign_document_type()

class dm_campaign_document(osv.osv):
    _name = 'dm.campaign.document'
    _columns = {
        'name' : fields.char('Name', size=64, required=True),
        'type_id' : fields.many2one('dm.campaign.document.type','Format',required=True),
        'segment_id' : fields.many2one('dm.campaign.proposition.segment','Segment',required=True),
    }
dm_campaign_document()

class Country(osv.osv):
    _name = 'res.country'
    _inherit = 'res.country'
    _columns = {
                'main_language' : fields.many2one('res.lang','Main Language',ondelete='cascade',),
                'main_currency' : fields.many2one('res.currency','Main Currency',ondelete='cascade'),
                'forwarding_charge' : fields.float('Forwarding Charge', digits=(16,2)),
                'payment_method_ids' : fields.many2many('account.journal','country_payment_method_rel','country_id','journal_id','Payment Methods',domain=[('type','=','cash')]),
    }
Country()

class res_partner(osv.osv):
    _name = "res.partner"
    _inherit="res.partner"
    _columns = {
        'country_ids' : fields.many2many('res.country', 'partner_country_rel', 'partner_id', 'country_id', 'Allowed Countries'),
        'state_ids' : fields.many2many('res.country.state','partner_state_rel', 'partner_id', 'state_id', 'Allowed States'),
        'dm_contact_id' : fields.many2one('res.partner.address', 'Address To Use', ondelete='cascade'),
    }
    def _default_category(self, cr, uid, context={}):
        if 'category_id' in context and context['category_id']:
            return [context['category_id']]
        elif 'category' in context and context['category']:
            id_cat = self.pool.get('res.partner.category').search(cr,uid,[('name','ilike',context['category'])])[0]
            return [id_cat]
        return []

    def _default_all_country(self, cr, uid, context={}):
        id_country = self.pool.get('res.country').search(cr,uid,[])
        return id_country

    def _default_all_state(self, cr, uid, context={}):
        id_state = self.pool.get('res.country.state').search(cr,uid,[])
        return id_state

    _defaults = {
        'category_id': _default_category,
        'country_ids': _default_all_country,
        'state_ids': _default_all_state,
    }
res_partner()

class res_partner_address(osv.osv):
    _inherit = 'res.partner.address'
    _columns = {
        'firstname' : fields.char('First Name',size=64),
        'name_complement' : fields.char('Name Complement',size=64),
        'street3' : fields.char('Street3',size=32),
        'street4' : fields.char('Street4',size=32),
    }
res_partner_address()

class purchase_order(osv.osv):
    _name = 'purchase.order'
    _inherit = 'purchase.order'
    _columns = {
        'dm_campaign_purchase_line' : fields.many2one('dm.campaign.purchase_line','DM Campaign Purchase Line'),
    }
purchase_order()

class project_task(osv.osv):
    _name = "project.task"
    _inherit = "project.task"
    context_data ={}

    def default_get(self, cr, uid, fields, context=None):
        if 'type' in context and 'project_id' in context:
            self.context_data = context.copy()
            self.context_data['flag'] = True
        else:
            self.context_data['flag'] = False
        return super(project_task, self).default_get(cr, uid, fields, context)

    def fields_view_get(self, cr, user, view_id=None, view_type='form', context=None, toolbar=False):
        result = super(project_task,self).fields_view_get(cr, user, view_id, view_type, context, toolbar)
        if 'flag' in self.context_data or 'type' in context:
            if 'project_id' in self.context_data:
                if result['type']=='form':
                    result['arch']= """<?xml version="1.0" encoding="utf-8"?>\n<form string="Task edition">\n<group colspan="6" col="6">\n<field name="name" select="1"/>\n<field name="project_id" readonly="1" select="1"/>\n
                        <field name="total_hours" widget="float_time"/>\n<field name="user_id" select="1"/>\n<field name="date_deadline" select="2"/>\n<field name="progress" widget="progressbar"/>\n</group>\n
                        <notebook colspan="4">\n<page string="Information">\n<field name="planned_hours" widget="float_time" on_change="onchange_planned(planned_hours,effective_hours)"/>\n<field name="delay_hours" widget="float_time"/>\n
                        <field name="remaining_hours" select="2" widget="float_time"/>\n<field name="effective_hours" widget="float_time"/>\n<field colspan="4" name="description" nolabel="1" select="2"/>\n
                        <field colspan="4" name="work_ids" nolabel="1"/>\n<newline/>\n<group col="11" colspan="4">\n<field name="state" select="1"/>\n<button name="do_draft" states="open" string="Set Draft" type="object"/>
                        <button name="do_open" states="pending,draft" string="Open" type="object"/>\n<button name="do_reopen" states="done,cancelled" string="Re-open" type="object"/>\n<button name="do_pending" states="open" string="Set Pending" type="object"/>\n
                        <button groups="base.group_extended" name="%(project.wizard_delegate_task)d" states="pending,open" string="Delegate" type="action"/>\n<button name="%(project.wizard_close_task)d" states="pending,open" string="Done" type="action"/>\n
                        <button name="do_cancel" states="draft,open,pending" string="Cancel" type="object"/>\n</group>\n</page>\n<page groups="base.group_extended" string="Delegations">\n
                        <field colspan="4" name="history" nolabel="1"/>\n<field colspan="4" height="150" name="child_ids" nolabel="1">\n<tree string="Delegated tasks">\n<field name="name"/>\n
                        <field name="user_id"/>\n<field name="date_deadline"/>\n<field name="planned_hours" widget="float_time"/>\n<field name="effective_hours" widget="float_time"/>\n<field name="state"/>\n</tree>\n
                        </field>\n<field colspan="4" name="parent_id"/>\n</page>\n<page groups="base.group_extended" string="Extra Info">\n<separator string="Planning" colspan="2"/>\n<separator string="Dates" colspan="2"/>\n<field name="priority"/>\n
                        <field name="date_start" select="2"/>\n<field name="sequence"/>\n<field name="date_close" select="2"/>\n<field name="type"/>\n<field name="active" select="2"/>\n
                        <field name="partner_id" select="2"/>\n<separator colspan="4" string="Notes"/>\n<field colspan="4" name="notes" nolabel="1"/>\n</page>\n</notebook>\n</form>"""
        return result
    
    def create(self,cr,uid,vals,context={}):
        if 'flag' in self.context_data:
            if 'type' in self.context_data:
                task_type = self.pool.get('project.task.type').search(cr,uid,[('name','=',self.context_data['type'])])[0]
                vals['type']=task_type
                vals['project_id']=self.context_data['project_id']
                self.context_data = {}
            if 'planned_hours' not in vals:
                vals['planned_hours'] = 0.0
        return super(project_task, self).create(cr, uid, vals, context)
    
    _columns = {
        'date_reviewed': fields.datetime('Reviewed Date'),
        'date_planned': fields.datetime('Planned Date'),
    }

project_task()



#vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
