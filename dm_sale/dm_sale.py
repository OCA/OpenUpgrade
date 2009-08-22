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


class dm_workitem(osv.osv):
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
        
dm_workitem()


class sale_order(osv.osv):#{{{
    _name = "sale.order"
    _inherit="sale.order"

    _columns = {
        'offer_step_id': fields.many2one('dm.offer.step','Offer Step'),
        'segment_id' : fields.many2one('dm.campaign.proposition.segment','Segment'),
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

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
