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
import sys
from osv import fields
from osv import osv
import netsvc
import traceback
import sys
import datetime

class dm_workitem(osv.osv): # {{{
    _name = "dm.workitem"
    _inherit = "dm.workitem"

    _columns = {
        'sale_order_id' : fields.many2one('sale.order','Sale Order'),
    }

    def run(self, cr, uid, wi, context={}):
        result = super(dm_workitem,self).run(cr, uid, wi, context)
        if wi.sale_order_id:
            so_res = self.pool.get('sale.order')._sale_order_process(cr, uid, wi.sale_order_id.id)
        return result

    def copy(self, cr, uid, id, default=None, context={}):
        if not default: default = {}
        default.update({'sale_order_id': False})
        copy_id = super(dm_workitem, self).copy(cr, uid, id, default, context)
        return copy_id
        
dm_workitem() # }}}

class dm_event_sale(osv.osv_memory): # {{{
    _name = "dm.event.sale"
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
        'is_realtime' : fields.boolean('Realtime Processing'),
    }
    _defaults = {
        'source': lambda *a: 'address_id',
        'sale_order_id' : lambda *a : False,
    }

    def create(self,cr,uid,vals,context={}):
        id = super(dm_event_sale,self).create(cr,uid,vals,context)
        obj = self.browse(cr, uid ,id)

        tr_ids = self.pool.get('dm.offer.step.transition').search(cr, uid, [('step_from_id','=',obj.step_id.id),
                ('condition_id','=',obj.trigger_type_id.id)])
        if not tr_ids:
            netsvc.Logger().notifyChannel('dm event case', netsvc.LOG_WARNING, "There is no transition %s at this step : %s"% (obj.trigger_type_id.name, obj.step_id.code))
            raise osv.except_osv('Warning', "There is no transition %s at this step : %s"% (obj.trigger_type_id.name, obj.step_id.code))
            return False
        for tr in self.pool.get('dm.offer.step.transition').browse(cr, uid, tr_ids):
            if obj.action_time:
                action_time = datetime.datetime.strptime(obj.action_time, '%Y-%m-%d  %H:%M:%S')
            else:
                if obj.is_realtime:
                    action_time = datetime.datetime.now()
                else:
                    wi_action_time = datetime.datetime.now()
                    kwargs = {(tr.delay_type+'s'): tr.delay}
                    action_time = wi_action_time + datetime.timedelta(**kwargs)

                    if tr.action_hour:
                        hour_str =  str(tr.action_hour).split('.')[0] + ':' + str(int(int(str(tr.action_hour).split('.')[1]) * 0.6))
                        act_hour = datetime.datetime.strptime(hour_str,'%H:%M')
                        action_time = action_time.replace(hour=act_hour.hour)
                        action_time = action_time.replace(minute=act_hour.minute)

                    if tr.action_day:
                        action_time = action_time.replace(day=int(tr.action_day))
                        if action_time.day > int(tr.action_day):
                            action_time = action_time.replace(month=action_time.month + 1)

                    if tr.action_date:
                        action_time = tr.action_date

            try:
                wi_id = self.pool.get('dm.workitem').create(cr, uid, {'step_id':tr.step_to_id.id or False, 'segment_id':obj.segment_id.id or False,
                'address_id':obj.address_id.id, 'mail_service_id':obj.mail_service_id.id, 'action_time':action_time.strftime('%Y-%m-%d  %H:%M:%S'),
                'tr_from_id':tr.id,'source':obj.source, 'is_realtime': obj.is_realtime, 'sale_order_id':obj.sale_order_id.id})
            except Exception, exception:
                tb = sys.exc_info()
                tb_s = "".join(traceback.format_exception(*tb))
                netsvc.Logger().notifyChannel('dm event sale', netsvc.LOG_ERROR, "Event cannot create Workitem : %s\n%s" % (str(exception), tb_s))
        return id

dm_event_sale() # }}}

class sale_order(osv.osv):#{{{
    _name = "sale.order"
    _inherit="sale.order"

    _columns = {
        'offer_step_id': fields.many2one('dm.offer.step', 'Offer Step', select="1"),
        'segment_id' : fields.many2one('dm.campaign.proposition.segment', 'Segment', select="1"),
        'journal_id': fields.many2one('account.journal', 'Journal'),
        'lines_number' : fields.integer('Number of sale order lines'),
        'so_confirm_do' : fields.boolean('Auto confirm sale order'),
        'invoice_create_do' : fields.boolean('Auto create invoice'),
        'invoice_validate_do' : fields.boolean('Auto validate invoice'),
        'invoice_pay_do' : fields.boolean('Auto pay invoice'),
    }

    def _sale_order_process(self, cr, uid, sale_order_id):
        so = self.pool.get('sale.order').browse(cr, uid, sale_order_id)
        wf_service = netsvc.LocalService('workflow')

        try:
            if so.so_confirm_do and so.state == 'draft':
                wf_service.trg_validate(uid, 'sale.order', sale_order_id, 'order_confirm', cr)
                if so.invoice_create_do:
                    inv_id = self.pool.get('sale.order').action_invoice_create(cr, uid, [sale_order_id])
                    if so.journal_id and so.journal_id.default_credit_account_id and so.journal_id.default_credit_account_id.reconcile:
                        self.pool.get('account.invoice').write(cr, uid, inv_id, {'journal_id': so.journal_id.id, 'account_id': so.journal_id.default_credit_account_id.id})
                    if inv_id and so.invoice_validate_do:
                        wf_service.trg_validate(uid, 'account.invoice', inv_id, 'invoice_open', cr)
                        if so.invoice_pay_do:
                            ids = self.pool.get('account.period').find(cr, uid, {})
                            period_id = False
                            if len(ids):
                                period_id = ids[0]

                            cur_obj = self.pool.get('res.currency')

                            for invoice in so.invoice_ids:
                                journal = invoice.journal_id
                                amount = invoice.residual
                                if journal.currency and invoice.company_id.currency_id.id<>journal.currency.id:
                                    ctx = {'date':time.strftime('%Y-%m-%d')}
                                    amount = cur_obj.compute(cr, uid, journal.currency.id, invoice.company_id.currency_id.id, amount, context=ctx)

                                acc_id = journal.default_credit_account_id and journal.default_credit_account_id.id
                                if not acc_id:
                                    raise osv.except_osv('Error !','Your journal must have a default credit and debit account.')
                                self.pool.get('account.invoice').pay_and_reconcile(cr, uid, [invoice.id],
                                            amount, acc_id, period_id, journal.id, '', '', '',)

        except Exception, exception:
            tb = sys.exc_info()
            tb_s = "".join(traceback.format_exception(*tb))
            self.write(cr, uid, [wi.id], {'state': 'error','error_msg':'Exception: %s\n%s' % (str(exception), tb_s)})
            netsvc.Logger().notifyChannel('dm action - so process', netsvc.LOG_ERROR, 'Exception: %s\n%s' % (str(exception), tb_s))

sale_order()#}}}

class dm_offer_step(osv.osv):
    _name = "dm.offer.step"
    _inherit = "dm.offer.step"
    
    _columns = {
        'forecasted_yield' : fields.float('Forecasted Yield'),
        'item_ids' : fields.many2many('product.product','dm_offer_step_product_rel','product_id','offer_step_id','Items', states={'closed':[('readonly',True)]}),
        }
dm_offer_step()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
