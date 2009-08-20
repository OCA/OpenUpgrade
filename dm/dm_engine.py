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

class dm_workitem(osv.osv): # {{{
    _name = "dm.workitem"
    _description = "workitem"
    _SOURCES = [('address_id','Partner Address')]
    SELECTION_LIST = [('pending','Pending'),('error','Error'),('cancel','Cancelled'),('done','Done')]
    _rec_name = 'step_id'

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
#                            amount_tax = invoice.residual
                            amount = invoice.residual
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

SYSMSG_STATES = [
    ('draft','Draft'),
    ('open','Open'),
    ('close','Close'),
    ('pending','Pending'),
    ('cancel','Cancelled'),
    ('done','Done'),
    ('error','Error'),
]

class dm_sysmsg(osv.osv):
    _name = "dm.sysmsg"

    def _default_model(self, cr, uid, context={}):
        return self.pool.get('ir.model').search(cr,uid,[('model','=','dm.workitem')])[0]

    def _default_field(self, cr, uid, context={}):
        return self.pool.get('ir.model.fields').search(cr,uid,[('model_id','=','workitem'),('name','=','error_msg')])[0]

    _columns = {
       'name' : fields.char('Description', translate=True, size=64, required=True),
       'code' : fields.char('Code', size=64, required=True),
       'message' : fields.text('Message', translate=True),
       'state' : fields.selection(SYSMSG_STATES, 'State to set'),
       'level' : fields.integer('Level'),
       'model' : fields.many2one('ir.model', 'Model', required=True),
       'field' : fields.many2one('ir.model.fields', 'Field', required=True),
       'send_email': fields.boolean('Send Email'),
       'email_user' : fields.many2one('res.users', 'Email User'),
       'result'  : fields.boolean('Action Result'),
    }
    _defaults = {
       'state' : lambda *a : 'error',
       'level' : lambda *a: 1,
       'model' : _default_model,
       'field' : _default_field,
    }
dm_sysmsg()

