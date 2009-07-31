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

class dm_order(osv.osv): # {{{
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

dm_order() # }}}

class res_partner(osv.osv): # {{{
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
res_partner() # }}}

class dm_workitem(osv.osv): # {{{
    _name = "dm.workitem"
    _description = "workitem"
    _SOURCES = [('address_id','Partner Address')]
    SELECTION_LIST = [('pending','Pending'),('error','Error'),('cancel','Cancelled'),('done','Done')]

    _columns = {
        'step_id' : fields.many2one('dm.offer.step', 'Offer Step', select="1", ondelete="cascade"),
        'segment_id' : fields.many2one('dm.campaign.proposition.segment', 'Segments', select="1", ondelete="cascade"),
        'address_id' : fields.many2one('res.partner.address', 'Customer Address', select="1", ondelete="cascade"),
        'action_time' : fields.datetime('Action Time'),
        'source' : fields.selection(_SOURCES, 'Source', required=True),
        'error_msg' : fields.text('System Message'),
        'is_global': fields.boolean('Global Workitem'),
        'is_preview': fields.boolean('Document Preview Workitem'),
        'use_prev_plugin_values': fields.boolean('Use Previous Plugin Values (For Document Regeneration)'),
        'tr_from_id' : fields.many2one('dm.offer.step.transition', 'Source Transition', select="1", ondelete="cascade"),
        'sale_order_id' : fields.many2one('sale.order','Sale Order'),
        'mail_service_id' : fields.many2one('dm.mail_service','Mail Service'),
        'state' : fields.selection(SELECTION_LIST, 'Status'),
    }
    _defaults = {
        'source': lambda *a: 'address_id',
        'state': lambda *a: 'pending',
        'is_global': lambda *a: False,
        'is_preview': lambda *a: False,
        'action_time' : lambda *a: time.strftime('%Y-%m-%d %H:%M:%S'),
    }


    def _check_sysmsg(self, cr, uid, ids, code):
        """ Check action message code and set workitem log """
        sysmsg_id  = self.pool.get('dm.sysmsg').search(cr, uid, [('code','=',code)])
        if sysmsg_id:
            sysmsg = self.pool.get('dm.sysmsg').browse(cr, uid, sysmsg_id)[0]
            self.write(cr, uid, [ids], {'state': sysmsg.state,'error_msg':sysmsg.message})
            return sysmsg.result
        else:
            self.write(cr, uid, [ids], {'state': 'error','error_msg':"An unknown error has occured : %s" % code})
            return False


    def _sale_order_process(self, cr, uid, sale_order_id):
        so = self.pool.get('sale.order').browse(cr, uid, sale_order_id)
        wf_service = netsvc.LocalService('workflow')

        if so.so_confirm_do and so.state == 'draft':
            wf_service.trg_validate(uid, 'sale.order', sale_order_id, 'order_confirm', cr)
            if so.invoice_create_do:
                inv_id = self.pool.get('sale.order').action_invoice_create(cr, uid, [sale_order_id])
                if so.journal_id:
                    self.pool.get('account.invoice').write(cr, uid, inv_id, {'journal_id': so.journal_id.id, 'account_id': so.journal_id.default_credit_account_id.id})
                if inv_id and so.invoice_validate_do:
                    wf_service.trg_validate(uid, 'account.invoice', inv_id, 'invoice_open', cr)
                    if so.invoice_pay_do:
                        ids = self.pool.get('account.period').find(cr, uid, {})
                        period_id = False
                        if len(ids):
                            period_id = ids[0]

                        cur_obj = self.pool.get('res.currency')
                        #journal = self.pool.get('account.journal').browse(cr, uid, journal_id, context)

                        for invoice in so.invoice_ids:
                            journal = invoice.journal_id
                            amount_tax = invoice.amount_tax
                            amount = invoice.amount_tax
                            if journal.currency and invoice.company_id.currency_id.id<>journal.currency.id:
                                ctx = {'date':time.strftime('%Y-%m-%d')}
                                amount = cur_obj.compute(cr, uid, journal.currency.id, invoice.company_id.currency_id.id, amount, context=ctx)

                            acc_id = journal.default_credit_account_id and journal.default_credit_account_id.id
                            if not acc_id:
                                raise osv.except_osv('Error !','Your journal must have a default credit and debit account.')
                            self.pool.get('account.invoice').pay_and_reconcile(cr, uid, [invoice.id],
                                        amount, acc_id, period_id, journal.id, '', '', '',)
        


    def run(self, cr, uid, wi, context={}):
        context['active_id'] = wi.id
        done = False
        ms_err = ''

        try:
            server_obj = self.pool.get('ir.actions.server')
            tr_res = True

            """ Check if action must be done or cancelled by checking the condition code of incoming transitions """
            for tr in wi.step_id.incoming_transition_ids:
                eval_context = {
                    'pool' : self.pool,
                    'cr' : cr,
                    'uid' : uid,
                    'wi': wi,
                    'tr' : tr,
                }
                val = {}

                """ Evaluate condition code (for non preview workitems only)"""
                if wi.is_preview:
                    val['action'] = True
                else:
                    exec tr.condition_id.in_act_cond.replace('\r','') in eval_context,val

                if not val.get('action', False):
                    """ If action returned by the trigger code is False stop here """
                    tr_res = False
                    act_step = tr.step_from_id.name or False
                    break

            if tr_res:
                """ Execute server action """
                res = server_obj.run(cr, uid, [wi.step_id.action_id.id], context)

                """ Check returned value and set done status """
                done = self._check_sysmsg(cr, uid, wi.id, res)

                """ Set workitem state as done """
                if done:
                    self.write(cr, uid, [wi.id], {'state': 'done','error_msg':""})
            else:
                """ Dont Execute Action if workitem is not to be processed """
                self.write(cr, uid, [wi.id], {'state': 'cancel','error_msg':'Cancelled by : %s'% act_step})
                done = False

        except Exception, exception:
            import traceback
            tb = sys.exc_info()
            tb_s = "".join(traceback.format_exception(*tb))
            self.write(cr, uid, [wi.id], {'state': 'error','error_msg':'Exception: %s\n%s' % (str(exception), tb_s)})
            netsvc.Logger().notifyChannel('dm action', netsvc.LOG_ERROR, 'Exception: %s\n%s' % (str(exception), tb_s))


        """ Check if it has to create next auto workitems """
        if done and not wi.is_preview:
            for tr in wi.step_id.outgoing_transition_ids:
                if tr.condition_id and tr.condition_id.gen_next_wi:

                    """ Compute action time """
                    wi_action_time = datetime.datetime.strptime(wi.action_time, '%Y-%m-%d  %H:%M:%S')
                    kwargs = {(tr.delay_type+'s'): tr.delay}
                    next_action_time = wi_action_time + datetime.timedelta(**kwargs)

                    if tr.action_hour:
                        """ If a static action hour is set, use it """
                        hour_str =  str(tr.action_hour).split('.')[0] + ':' + str(int(int(str(tr.action_hour).split('.')[1]) * 0.6))
                        act_hour = datetime.datetime.strptime(hour_str,'%H:%M')
                        next_action_time = next_action_time.replace(hour=act_hour.hour)
                        next_action_time = next_action_time.replace(minute=act_hour.minute)

                    if tr.action_day:
                        """ If a static action day of the month is set, use it """
                        next_action_time = next_action_time.replace(day=int(tr.action_day))
                        if next_action_time.day > int(tr.action_day):
                            next_action_time = next_action_time.replace(month=next_action_time.month + 1)

                    if tr.action_date:
                        """ If a static date is set, use it """
                        next_action_time = tr.action_date

                    try:
                        aw_id = self.copy(cr, uid, wi.id, {'step_id':tr.step_to_id.id, 'tr_from_id':tr.id,
                            'action_time':next_action_time.strftime('%Y-%m-%d  %H:%M:%S'), 'sale_order_id': False})
                        netsvc.Logger().notifyChannel('dm action', netsvc.LOG_DEBUG, "Creating Auto Workitem %d with action at %s"% (aw_id,next_action_time.strftime('%Y-%m-%d  %H:%M:%S')))
                    except:
                        netsvc.Logger().notifyChannel('dm action', netsvc.LOG_ERROR, "Cannot create Auto Workitem")
        
        """ Processing sale orders """
        if wi.sale_order_id:
            so_res = self._sale_order_process(cr, uid, wi.sale_order_id.id)

        return True

    def __init__(self, *args):
        self.is_running = False
        return super(dm_workitem, self).__init__(*args)

    def mail_service_run(self, cr, uid, camp_doc, context={}):
        context['active_id'] = camp_doc.id
        try:
            server_obj = self.pool.get('ir.actions.server')
            res = server_obj.run(cr, uid, [camp_doc.mail_service_id.action_id.id], context)
            camp_res = self.pool.get('dm.campaign.document').read(cr, uid, [camp_doc.id], ['state'])[0]

            """ If no error occured during the document delivery set state to done """
            if camp_res['state'] != 'error':
                self.pool.get('dm.campaign.document').write(cr, uid, [camp_doc.id], {'state':'done','delivery_time':time.strftime('%Y-%m-%d %H:%M:%S'),'error_msg':""})

        except Exception, exception:
            import traceback
            tb = sys.exc_info()
            tb_s = "".join(traceback.format_exception(*tb))
            self.pool.get('dm.campaign.document').write(cr, uid, [camp_doc.id], {'state': 'error','error_msg':'Exception: %s\n%s' % (str(exception), tb_s)})
            netsvc.Logger().notifyChannel('dm campaign document', netsvc.LOG_ERROR, 'Exception: %s\n%s' % (str(exception), tb_s))

        return True

    def check_all(self, cr, uid, context={}):
        """ Check if the action engine is already running """
        if not self.is_running:
            self.is_running = True

            """ Workitems processing """
            """ Get workitems to process """
            ids = self.search(cr, uid, [('state','=','pending'),('action_time','<=',time.strftime('%Y-%m-%d %H:%M:%S'))])

            """ Run workitem action """
            for wi in self.browse(cr, uid, ids, context=context):
                wi_res = self.run(cr, uid, wi, context=context)
            

            """ Campaign documents processing """
            """ Get campaign documents to process """
            camp_doc_obj = self.pool.get('dm.campaign.document')
            camp_doc_ids = camp_doc_obj.search(cr, uid, [('state','=','pending')])

            """ Run campaign document action """
            for camp_doc in camp_doc_obj.browse(cr, uid, camp_doc_ids, context=context):
                ms_res = self.mail_service_run(cr, uid, camp_doc, context=context)

            self.is_running = False
            return True
        return False

dm_workitem() # }}}

class dm_customer_segmentation(osv.osv): # {{{
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

dm_customer_segmentation() # }}}

TEXT_OPERATORS = [ # {{{
    ('like','like'),
    ('ilike','ilike'),
] # }}}

NUMERIC_OPERATORS = [ # {{{
    ('=','equals'),
    ('<','smaller then'),
    ('>','bigger then'),
] # }}}

BOOL_OPERATORS = [ # {{{
    ('is','is'),
    ('isnot','is not'),
] # }}}

DATE_OPERATORS = [ # {{{
    ('=','equals'),
    ('<','before'),
    ('>','after'),
] # }}}

class dm_customer_text_criteria(osv.osv): # {{{
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
dm_customer_text_criteria() # }}}

class dm_customer_numeric_criteria(osv.osv): # {{{
    _name = "dm.customer.numeric_criteria"
    _description = "Customer Segmentation Numeric Criteria"
    _rec_name = "segmentation_id"

    _columns = {
        'segmentation_id' : fields.many2one('dm.customer.segmentation', 'Segmentation'),
        'field_id' : fields.many2one('ir.model.fields','Customers Field',
               domain=[('model_id.model','=','res.partner'),
               ('ttype','in',['integer','float'])],
               context={'model':'res.partner'}),
        'operator' : fields.selection(NUMERIC_OPERATORS, 'Operator', size=32),
        'value' : fields.float('Value', digits=(16,2)),
    }
dm_customer_numeric_criteria() # }}}

class dm_customer_boolean_criteria(osv.osv): # {{{
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
dm_customer_boolean_criteria() # }}}

class dm_customer_date_criteria(osv.osv): # {{{
    _name = "dm.customer.date_criteria"
    _description = "Customer Segmentation Date Criteria"
    _rec_name = "segmentation_id"

    _columns = {
        'segmentation_id' : fields.many2one('dm.customer.segmentation', 'Segmentation'),
        'field_id' : fields.many2one('ir.model.fields','Customers Field',
               domain=[('model_id.model','=','res.partner'),
               ('ttype','in',['date','datetime'])],
               context={'model':'res.partner'}),
        'operator' : fields.selection(DATE_OPERATORS, 'Operator', size=32),
        'value' : fields.date('Date'),
    }
dm_customer_date_criteria() # }}}

class dm_customer_order_text_criteria(osv.osv): # {{{
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
dm_customer_order_text_criteria() # }}}

class dm_customer_order_numeric_criteria(osv.osv): # {{{
    _name = "dm.customer.order.numeric_criteria"
    _description = "Customer Order Segmentation Numeric Criteria"
    _rec_name = "segmentation_id"

    _columns = {
        'segmentation_id' : fields.many2one('dm.customer.segmentation', 'Segmentation'),
        'field_id' : fields.many2one('ir.model.fields','Customers Field',
               domain=[('model_id.model','=','dm.customer.order'),
               ('ttype','in',['integer','float'])],
               context={'model':'dm.customer.order'}),
        'operator' : fields.selection(NUMERIC_OPERATORS, 'Operator', size=32),
        'value' : fields.float('Value', digits=(16,2)),
    }
dm_customer_order_numeric_criteria() # }}}

class dm_customer_order_boolean_criteria(osv.osv): # {{{
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
dm_customer_order_boolean_criteria() # }}}

class dm_customer_order_date_criteria(osv.osv): # {{{
    _name = "dm.customer.order.date_criteria"
    _description = "Customer Order Segmentation Date Criteria"
    _rec_name = "segmentation_id"

    _columns = {
        'segmentation_id' : fields.many2one('dm.customer.segmentation', 'Segmentation'),
        'field_id' : fields.many2one('ir.model.fields','Customers Field',
               domain=[('model_id.model','=','dm.customer.order'),
               ('ttype','in',['date','datetime'])],
               context={'model':'dm.customer.order'}),
        'operator' : fields.selection(DATE_OPERATORS, 'Operator', size=32),
        'value' : fields.date('Date'),
    }
dm_customer_order_date_criteria() # }}}

class dm_offer_history(osv.osv): # {{{
    _name = "dm.offer.history"
    _order = 'date'
    _columns = {
        'offer_id' : fields.many2one('dm.offer', 'Offer', required=True, ondelete="cascade"),
        'date' : fields.date('Drop Date'),
        'campaign_id' : fields.many2one('dm.campaign','Name', ondelete="cascade"),
        'code' : fields.char('Code', size=16),
        'responsible_id' : fields.many2one('res.users','Responsible'),
    }
dm_offer_history() # }}}

class dm_event(osv.osv_memory): # {{{
    _name = "dm.event"
    _rec_name = "segment_id"

    _columns = {
        'segment_id' : fields.many2one('dm.campaign.proposition.segment', 'Segment', required=True),
        'step_id' : fields.many2one('dm.offer.step', 'Offer Step', required=True),
        'source' : fields.selection([('address_id','Addresses')], 'Source', required=True),
        'address_id' : fields.many2one('res.partner.address', 'Address'),
        'trigger_type_id' : fields.many2one('dm.offer.step.transition.trigger','Trigger Condition',required=True),
        'sale_order_id' : fields.many2one('sale.order', 'Sale Order'),
        'mail_service_id' : fields.many2one('dm.mail_service','Mail Service'),
        'action_time': fields.datetime('Action Time'),
    }
    _defaults = {
        'source': lambda *a: 'address_id',
        'sale_order_id' : lambda *a : False,
    }

    def create(self,cr,uid,vals,context={}):
        id = super(dm_event,self).create(cr,uid,vals,context)
        obj = self.browse(cr, uid ,id)
        tr_ids = self.pool.get('dm.offer.step.transition').search(cr, uid, [('step_from_id','=',obj.step_id.id),
                ('condition_id','=',obj.trigger_type_id.id)])
        if not tr_ids:
            netsvc.Logger().notifyChannel('dm event case', netsvc.LOG_WARNING, "There is no transition %s at this step : %s"% (obj.trigger_type_id.name, obj.step_id.code))
            osv.except_osv('Warning', "There is no transition %s at this step : %s"% (obj.trigger_type_id.name, obj.step_id.code))
            return False

        for tr in self.pool.get('dm.offer.step.transition').browse(cr, uid, tr_ids):
            if obj.action_time:
                next_action_time = datetime.datetime.strptime(obj.action_time, '%Y-%m-%d  %H:%M:%S')
            else:
                wi_action_time = datetime.datetime.now()
                kwargs = {(tr.delay_type+'s'): tr.delay}
                next_action_time = wi_action_time + datetime.timedelta(**kwargs)

                if tr.action_hour:
                    hour_str =  str(tr.action_hour).split('.')[0] + ':' + str(int(int(str(tr.action_hour).split('.')[1]) * 0.6))
                    act_hour = datetime.datetime.strptime(hour_str,'%H:%M')
                    next_action_time = next_action_time.replace(hour=act_hour.hour)
                    next_action_time = next_action_time.replace(minute=act_hour.minute)

                if tr.action_day:
                    next_action_time = next_action_time.replace(day=int(tr.action_day))
                    if next_action_time.day > int(tr.action_day):
                        next_action_time = next_action_time.replace(month=next_action_time.month + 1)

                if tr.action_date:
                    next_action_time = tr.action_date

            try:
                wi_id = self.pool.get('dm.workitem').create(cr, uid, {'step_id':tr.step_to_id.id or False, 'segment_id':obj.segment_id.id or False,
                'address_id':obj.address_id.id, 'mail_service_id':obj.mail_service_id.id, 'action_time':next_action_time.strftime('%Y-%m-%d  %H:%M:%S'),
                'tr_from_id':tr.id,'source':obj.source, 'sale_order_id':obj.sale_order_id.id})
                netsvc.Logger().notifyChannel('dm event', netsvc.LOG_DEBUG, "Creating Workitem with action at %s"% next_action_time.strftime('%Y-%m-%d  %H:%M:%S'))
            except Exception, exception:
                import traceback
                tb = sys.exc_info()
                tb_s = "".join(traceback.format_exception(*tb))
                netsvc.Logger().notifyChannel('dm event', netsvc.LOG_ERROR, "Event cannot create Workitem : %s\n%s" % (str(exception), tb_s))
        return id

dm_event() # }}}
"""
class sale_order(osv.osv): # {{{
    _name = "sale.order"
    _inherit = "sale.order"
    _columns ={
        'offer_step_id' : fields.many2one('dm.offer.step','Offer Step'),
        'segment_id' : fields.many2one('dm.campaign.proposition.segment','Segment'),
        'journal_id': fields.many2one('account.journal', 'Journal'),
        'lines_number' : fields.integer('Number of sale order lines'),
        'so_confirm_do' : fields.boolean('Auto confirm sale order'),
        'invoice_create_do' : fields.boolean('Auto create invoice'),
        'invoice_validate_do' : fields.boolean('Auto validate invoice'),
        'invoice_pay_do' : fields.boolean('Auto pay invoice'),
    }
sale_order() # }}}
"""
