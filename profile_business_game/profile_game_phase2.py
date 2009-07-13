# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>). All Rights Reserved
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
from osv import fields, osv
import pooler
import time
import datetime
import mx.DateTime
from mx.DateTime import RelativeDateTime, now, DateTime, localtime
import math
from datetime import date
import netsvc
import random

# develop following dashboard
#Financial Manager (Fabien Pinckaers, put here the name of the financial manager user)
#-----------------

#Expenses Forecast: _________
#Current Treasory: _________

#Loans : [ button : Ask for a Loan ]
#* Total to Reimburse : ______
#* To Reimburse this Year : _____

#Directeur RH (Marc Dupont)
#--------------------------

#HR Budget : ________
#Budget Spread of the Year: (one2many on a account.budget)
#    Budget     | Amount

#Sales Manager (Stephane Dubois)
#-------------------------------

#Sales Y-1 : _______
#Sales Forecast : _______
#Margin Forecast : ________

#Logistic Manager (Marc Andre)
#-----------------------------

#Average Stock Y-1  : ______
#Average Stock Forecast : ____
#Costs of Purchases Forecast : _______

#Objectives Achievement (colspan=4)
#----------------------

#Turnover Y-1 : _____ | Total Benefits : _____ | # of Products Sold : __
#Turnover Growth : __ | Benefits Growth: _____ | Growth Products : _____
#Selected Objective: Maximise Turnover         | Current Note : 12/20, B


#Total Expenses, Total Treasury, Total Expenses Y-1; are computed functions that
#compute the balance of accounts of a particular type for the year defined in
#the context (fiscalyear). If no year is defined in the context, it's the
#current fiscal year. When I say Y-1, it means, current fiscalyear minus 1 year.

class bank_loan(osv.osv):
    _name = "bank.loan"
    _description = "Bank Loan"

    def onchange_loan_duration(self, cr, uid, ids, loan_duration = 3.0, loan_amount = 10000.0, rate = 8.0, context={}):
        amt = loan_amount * pow(((100 + rate)/100),loan_duration)
        return {'value':{'total_amount': amt }}

    def _compute(self, cr, uid, ids,field_name, args, context={}):
        res = {}
        for rec in self.browse(cr, uid, ids):
            amt = rec.loan_amount * pow(((100 + rec.rate)/100),rec.loan_duration)
            res[rec.id] = amt
        return res

    def get_loan(self, cr, uid, ids, context):
         res = {}
         fiscal_obj = self.pool.get('account.fiscalyear')
         fiscalyear_id = fiscal_obj.search(cr, uid, [('state','=','draft')])
         fy = int(fiscal_obj.browse(cr,uid,fiscalyear_id)[0].code)
         dt = datetime.date(fy,01,int(time.strftime('%d'))).strftime('%Y-%m-%d')
         journal = self.pool.get('account.journal').search(cr,uid,[('type','=','cash')])[0]
         period = self.pool.get('account.period').search(cr, uid, [('fiscalyear_id', 'in', fiscalyear_id)])[0]

         for rec in self.browse(cr, uid, ids):
            res['reimburse_principle_amt_without_int'] = (rec.loan_amount / (rec.loan_duration * 12))
            res['reimburse_principle_amt_with_int'] = (rec.total_amount / (rec.loan_duration * 12))
            res['interest_per_month'] = res['reimburse_principle_amt_with_int'] - res['reimburse_principle_amt_without_int']
            res['months_left'] = rec.loan_duration * 12
            self.write(cr, uid, rec.id, res)
            move_id = self.pool.get('account.move').create(cr, uid,{'period_id':period,'journal_id':journal})
            for code in ('161000','512100'):
                if code == '161000':
                    credit = rec.loan_amount
                    debit = 0.0
                else:
                    credit = 0.0
                    debit = rec.loan_amount
                acc_id = self.pool.get('account.account').search(cr, uid, [('code','=',code)])
                self.pool.get('account.move.line').create(cr, uid, {'name' : 'Bank Loan','date':dt,'account_id':acc_id[0],
                                    'credit':credit ,'debit': debit,'date_created':dt,'move_id':move_id})
            self.pool.get('account.move').post(cr, uid, [move_id], context)

         return {
                'type': 'ir.actions.act_window_close',
                }


    _columns = {
                'name':fields.char('Name',size=64),
                'fiscal_year':fields.many2one('account.fiscalyear', 'Fiscal Year', required=True, readonly=True, help="Year in which loan is taken"),
                'loan_duration' : fields.float('# of Years', help="Loan duration in years"),
                'loan_amount' : fields.float('Loan Amount',  help="Loan Amount"),
                'rate' : fields.float('Interest Rate',help="Interest Rate",readonly=True),
                'total_amount' : fields.function(_compute,method = True,  store= True, string ='Total Amount', help="Total Amount to be paid",readonly=True),
                'reimburse_principle_amt_without_int' : fields.float('Reimburse amount[without Interest]',  help="Reimburse loan amount per month without interest"),
                'reimburse_principle_amt_with_int' : fields.float('Reimburse amount [with Interest]', help="Reimburse loan amount per month with interest"),
                'interest_per_month' : fields.float('Interest amount per month', help="Interest amount per month"),
                'months_left' : fields.float('# of months left', help="Number of months left"),
                }
    _defaults = {
        'loan_duration' : lambda *a: 3.0,
        'loan_amount' : lambda *a: 10000.0,
        'rate' : lambda *a: 8.0,
        'fiscal_year':lambda self, cr, uid, context=None:\
        self.pool.get('account.fiscalyear').search(cr, uid, [('state','=','draft')])[0]
            }

bank_loan()

class profile_game_phase_two(osv.osv):
    _name="profile.game.phase2"

    def fields_view_get(self, cr, uid, view_id=None, view_type='form', context={}, toolbar=False, submenu=False):
        res = super(profile_game_phase_two, self).fields_view_get(cr, uid, view_id, view_type, context=context, toolbar=toolbar, submenu=submenu)
        p_id = self.search(cr, uid, [])
        p_br = self.browse(cr, uid, p_id)
        for rec in p_br:
            if rec.sales_user_id.name or False:
                hr_name = " "
                if rec.hr_user_id:
                   hr_name = rec.hr_user_id.name
                res['arch'] = res['arch'].replace('(SM)', rec.sales_user_id.name)
                res['arch'] = res['arch'].replace('(HRM)',hr_name)
                res['arch'] = res['arch'].replace('(FM)',rec.finance_user_id.name)
                res['arch'] = res['arch'].replace('(LM)', rec.logistic_user_id.name)
                return res
        res['arch'] = res['arch'].replace('(SM)',"")
        res['arch'] = res['arch'].replace('(HRM)',"")
        res['arch'] = res['arch'].replace('(FM)',"")
        res['arch'] = res['arch'].replace('(LM)',"")
        return res


    def _calculate_detail(self, cr, uid, ids, field_names, arg, context):
        res = {}
        fiscal_obj = self.pool.get('account.fiscalyear')
        account_obj = self.pool.get('account.account')
        next_fy = fiscal_obj.search(cr, uid, [('state','=','draft')])[0]
        nextyear = fiscal_obj.browse(cr,uid,next_fy)
        curr_fy = fiscal_obj.search(cr, uid, [('code','ilike', str(int(nextyear.code) - 1))])
        prev_fy = fiscal_obj.search(cr, uid, [('code','ilike', str(int(nextyear.code) - 2))])
        year_list = []
        if (curr_fy or False):
            year_list.append(curr_fy[0])
            curryear = fiscal_obj.browse(cr,uid,curr_fy)[0]
        if (prev_fy or False):
            year_list.append(prev_fy[0])
        phase2_obj = self.browse(cr, uid, ids, context=context)[0]
        res[phase2_obj.id] = {}
        last_total_sale = sale_forcast = margin_forcast = last_turnover = 0.0
        total_sold_products = total_benefit = cost_purchase_forcast = 0.0
        last_total_purchase = prev_prod_sold = prev_benefit = 0.0
        prev_turnover = 0.0
        for field in field_names:
            if field == 'hr_budget':
                res[phase2_obj.id][field] = 0.0
            if field ==  'avg_stock_forcast':
                res[phase2_obj.id][field] = 0.0

            if field == 'loan_total_reimburse' or field == 'loan_total_reimburse_this_year':
                total = 0.0
                bank_obj = self.pool.get('bank.loan')
                if field == 'loan_total_reimburse':
                    domain = []
                else:
                    domain = [('fiscal_year','=',next_fy)]
                total_year = bank_obj.search(cr, uid, domain)

                for loan in bank_obj.browse(cr, uid, total_year):
                    total += loan.loan_amount
                res[phase2_obj.id][field] = total
            if field == 'total_reimburse' or field == 'current_treasury':
                if curr_fy or False:
                    context = {'fiscalyear': curr_fy[0] or False,'target_move':'all'}
                    total = 0.0
                    if field == 'total_reimburse':
                        domain = [('user_type','ilike','payable')]
                    else:
                        domain = [('user_type','ilike','cash')]
                    account_ids = account_obj.search(cr,uid,domain)
                    for acc in  account_obj.browse(cr, uid, account_ids, context):
                           total += acc.balance
                    res[phase2_obj.id][field] = total
                else:
                    res[phase2_obj.id][field] = 0.0
            if field == 'last_total_sale':
                if curr_fy or False:
                    account_ids = account_obj.search(cr,uid,[('code','ilike','Classe_7')])
                    for fy in year_list:
                        context = {'fiscalyear': fy,'target_move':'all'}
                        account = account_obj.browse(cr,uid,account_ids[0], context)
                        if fy == curr_fy[0]:
                            last_turnover = last_total_sale = account.balance
                            res[phase2_obj.id]['last_total_sale'] = last_total_sale
                            res[phase2_obj.id]['last_turnover'] = last_turnover
                        else:
                            prev_turnover = account.balance
                    res[phase2_obj.id]['turnover_growth'] =  (last_turnover or 0.0) - (prev_turnover or 0.0)
                else:
                    res[phase2_obj.id]['last_total_sale'] = 0.0
                    res[phase2_obj.id]['last_turnover'] = 0.0
                    res[phase2_obj.id]['turnover_growth'] = 0.0

            if field == 'sale_forcast' or field == 'margin_forcast':
                if curr_fy or False:
                    forecast_obj = self.pool.get('stock.planning.sale.prevision')
                    period_id = self.pool.get('stock.period').search(cr, uid, [('name', 'ilike',curryear.code)])
                    forecast_ids = forecast_obj.search(cr, uid, [('period_id', 'in', period_id)])
                    for value in forecast_obj.browse(cr ,uid, forecast_ids):
                        if field == 'sale_forcast':
                            sale_forcast += value.product_amt
                            res[phase2_obj.id][field] = sale_forcast
                        else:
                            margin_forcast += value.product_amt - (value.product_qty * value.product_id.standard_price)
                            res[phase2_obj.id][field] = margin_forcast
                else:
                    res[phase2_obj.id][field] = 0.0

            if field == 'total_sold_products' or field == 'last_total_purchase':
                res[phase2_obj.id]['products_growth'] = 0.0
                if field == 'total_sold_products':
                    years = year_list
                    type = 'out_invoice'
                else:
                    years = curr_fy or []
                    type = 'in_invoice'
                i = 0
                total_balance = [0,0]
                for fy in fiscal_obj.browse(cr,uid, years):
                    sql="""
                        select
                        sum(invoice_line.quantity) as total
                        from account_invoice_line invoice_line
                        where invoice_line.invoice_id in (select id from account_invoice invoice
                        where invoice.type ='%s' and date_invoice>='%s' and date_invoice<='%s')
                        """%(type,fy.date_start,fy.date_stop)
                    cr.execute(sql)
                    result = cr.fetchall()[0]
                    total_balance[i] = result[0] or 0.0
                    i += 1
                if i <= 1:
                    last_total_purchase =  total_balance[0] or 0.0
                    res[phase2_obj.id][field] = last_total_purchase
                else:
                     total_sold_products =  total_balance[0]
                     prev_prod_sold = total_balance[1]
                     res[phase2_obj.id][field] = total_sold_products
                     res[phase2_obj.id]['products_growth'] = (total_sold_products or 0.0) - (prev_prod_sold or 0.0)

            if field == 'total_benefit':
                if curr_fy or False:
                    account_ids = account_obj.search(cr,uid,[('code','ilike','Classe_6')])
                    for fy in year_list:
                        context = {'fiscalyear': fy,'target_move':'all'}
                        account = account_obj.browse(cr,uid,account_ids[0], context)
                        if fy == curr_fy[0]:
                            total_benefit = (last_turnover or 0.0) - (account.balance or 0.0)
                            res[phase2_obj.id][field] = total_benefit
                        else:
                            prev_benefit = (prev_turnover or 0.0) -  (account.balance or 0.0)
                    res[phase2_obj.id]['benefits_growth'] = (total_benefit or 0.0) - (prev_benefit or 0.0)
                else:
                    res[phase2_obj.id][field] = 0.0
                    res[phase2_obj.id]['benefits_growth'] = 0.0

            if field == 'cost_purchase_forcast':
                if curr_fy or False:
                    forecast_obj = self.pool.get('stock.planning.sale.prevision')
                    period_id = self.pool.get('stock.period').search(cr, uid, [('name', 'ilike',curryear.code)])
                    forecast_ids = forecast_obj.search(cr, uid, [('period_id', 'in', period_id)])
                    stock_ids = self.pool.get('stock.planning').search(cr, uid, [('period_id','in', period_id)])
                    sum1 = 0.0
                    sum2 = 0.0
                    for stock in self.pool.get('stock.planning').browse(cr, uid,stock_ids):
                        sum1 += stock.incoming_left * stock.product_id.standard_price
                    for forecast in self.pool.get('stock.planning.sale.prevision').browse(cr, uid, forecast_ids):
                        sum2 += forecast.product_qty * forecast.product_id.standard_price
                    cost_purchase_forcast = sum1 + sum2
                    res[phase2_obj.id][field] = cost_purchase_forcast
                else:
                    res[phase2_obj.id][field] = 0.0
        return res

    _columns = {
        'name':fields.char('Name',size=64),
        'state':fields.selection([('3','3'),('4','4')],'Number of Players'),
        'finance_user_id':fields.many2one('res.users','Name of Financial Manager',readonly=True),
        'logistic_user_id':fields.many2one('res.users','Name of Logistic Manager', readonly=True),
        'sales_user_id':fields.many2one('res.users','Name of Sales Manager',readonly=True),
        'hr_user_id':fields.many2one('res.users','Name of HR Manager',readonly=True,invisible=False),
        'objectives':fields.selection([
            ('on_max_turnover','Maximise Turnover of Last Year'),
            ('on_max_cumulative','Maximise Cumulative Benefit'),
            ('on_max_products_sold','Maximise Number of Products Sold')],'Objectives'),
        'years':fields.selection([
            ('3','3 Years (40 minutes)'),
            ('5','5 Years (1 hour)'),
            ('7','7 Years (1 hours and 20 minutes)')],'Number of Turns'),
        'difficulty':fields.selection([
            ('easy','Easy'),
            ('medium','Medium'),
            ('hard','Hard')],'Difficulty'),
        'current_treasury' : fields.function(_calculate_detail, method=True, type='float', string='Current treasury', multi='all',help="Balance of all Cash Accounts"),
        'total_reimburse' : fields.function(_calculate_detail, method=True, type='float', string='Total to Reimburse', multi='all',help="Total to Reimburse"),
        'loan_total_reimburse' : fields.function(_calculate_detail, method=True, type='float', string='Total to Reimburse', readonly=True, multi='all', help="Total loan amount to reimburse "),
        'loan_total_reimburse_this_year' : fields.function(_calculate_detail, method=True, type='float', string='Total to Reimburse this year', multi='all', readonly=True, help="Total loan amount to reimburse this year"),
        'hr_budget' : fields.function(_calculate_detail, method=True, type='float', string='HR Budget', multi='all',help="HR Budget"),
        'last_total_sale' : fields.function(_calculate_detail, method=True, type='float', string='Total Sales in Last Year', multi='all',help="Total Sales in Last Year"),
        'sale_forcast' : fields.function(_calculate_detail, method=True, type='float', string='Sales Forcast', multi='all',help="Sales Forcast"),
        'margin_forcast' : fields.function(_calculate_detail, method=True, type='float', string='Margin Forcast', multi='all',help="Margin Forcast"),
        'last_total_purchase' : fields.function(_calculate_detail, method=True, type='float', string='Total Purchases in Last year', multi='all',help="Total Purchases in Last year"),
        'avg_stock_forcast' : fields.function(_calculate_detail, method=True, type='float', string='Avg. Stock Forcast', multi='all',help="Avg. Stock Forcast"),
        'cost_purchase_forcast' : fields.function(_calculate_detail, method=True, type='float', string='Costs of Purchases Forecast', multi='all',help="Costs of Purchases Forecast"),
        'last_turnover' : fields.function(_calculate_detail, method=True, type='float', string='Turnover in last year', multi='all', help="Turnover in last year"),
        'total_sold_products' : fields.function(_calculate_detail, method=True, type='float', string='# of Products Sold', multi='all',help="# of Products Sold"),
        'turnover_growth' : fields.function(_calculate_detail, method=True, type='float', string='Turnover Growth', multi='all',help="Turnover Growth"),
        'benefits_growth' : fields.function(_calculate_detail, method=True, type='float', string='Benefits Growth', multi='all',help="Benefits Growth"),
        'total_benefit' : fields.function(_calculate_detail, method=True, type='float', string='Total Benefits', multi='all',help="Total Benefits"),
        'products_growth' : fields.function(_calculate_detail, method=True, type='float', string='Growth Products', multi='all',help="Growth Products"),
        'cy_traceback':fields.text('Traceback [Current Year]'),
        'warn_error':fields.text('Warnings & Errors'),
        'ay_traceback':fields.text('Traceback [All Years]'),
    }

    def pay_supplier_invoice(self, cr, uid, ids, context):
        print "pay_supplier_invoice"
        od = self.get_date(cr, uid,context)
        acc_obj = self.pool.get('account.account')
        acc_type_obj = self.pool.get('account.account.type')
        cash_acc_id = acc_type_obj.search(cr,uid,[('name','=','Cash')])
        acc_ids = acc_obj.search(cr,uid,[('user_type','in',cash_acc_id)])
        acc_br = acc_obj.browse(cr,uid,acc_ids)
        sum = 0
        for acc in acc_br:
            sum += acc.balance
        inv_obj = self.pool.get('account.invoice')
        open_inv_id = inv_obj.search(cr,uid,[('state','=','open'),('type','=','in_invoice')])
        inv_br = inv_obj.browse(cr,uid,open_inv_id)
        sum1=0
        for inv in inv_br:
            sum1 += inv.amount_total
        if sum1 > sum:
            msg = 'You do not have sufficient balance in your accounts to pay Supplier Invoices \n'\
                  'Balance : %s \n' \
                  'Amount to be paid :%s' % (sum,sum1)
            self.update_messages(cr, uid, ids, msg, context)
        journal = self.pool.get('account.journal').search(cr,uid,[('type','=','cash')])
        jour_br = self.pool.get('account.journal').browse(cr,uid,journal)
        for journl in jour_br:
            temp_bal = journl.default_debit_account_id.balance
            open_inv_id = inv_obj.search(cr,uid,[('state','=','open'),('type','=','in_invoice')])
            inv_br = inv_obj.browse(cr,uid,open_inv_id)
            for inv in inv_br:
                if temp_bal >= inv.amount_total:
                    self._pay_and_reconcile(cr, uid, ids, inv.id, journl.id, inv.amount_total, od, context)
                    temp_bal = temp_bal-inv.amount_total
        return True

    def _pay_and_reconcile(self, cr, uid, ids, invoice_id, journal_id, amount, od, context):
        print "_pay_and_reconcile"
        p_ids = self.pool.get('account.period').find(cr, uid, od, context=context)
        period_id = False
        if len(p_ids):
           period_id = p_ids[0]
        writeoff_account_id = False
        writeoff_journal_id = False
        cur_obj = self.pool.get('res.currency')

        invoice = self.pool.get('account.invoice').browse(cr, uid, invoice_id, context)
        journal = self.pool.get('account.journal').browse(cr, uid, journal_id, context)
        if journal.currency and invoice.company_id.currency_id.id<>journal.currency.id:
            ctx = {'date':self.get_date(cr, uid,context)}
            amount = cur_obj.compute(cr, uid, journal.currency.id, invoice.company_id.currency_id.id, amount, context=ctx)
        acc_id = journal.default_credit_account_id and journal.default_credit_account_id.id
        if not acc_id:
            msg = 'Your journal do not have a default credit and debit account.'
            self.update_messages(cr, uid, ids, msg, context)
        self.pool.get('account.invoice').pay_and_reconcile(cr, uid, [invoice_id],
                amount, acc_id, period_id, journal_id, False,
                period_id, False, context, invoice.origin)
        return True

    def confirm_draft_po(self, cr, uid, ids, context):
        print "confirm_draft_po"
        wf_service = netsvc.LocalService('workflow')
        po_obj = self.pool.get('purchase.order')
        po_ids = po_obj.search(cr,uid,[('state','=','draft')])
        for id in po_ids:
            brow_po = po_obj.browse(cr,uid,id)
            unpaid_inv_id = self.pool.get('account.invoice').search(cr,uid,[('state','!=','draft'),('reconciled','=',False),('partner_id','=',brow_po.partner_id.id),('type','=','in_invoice')])
            if len(unpaid_inv_id):
                msg = 'There are unpaid Supplier Invoice for the Supplier: "%s"'%(brow_po.partner_id.name,)
                self.update_messages(cr, uid, ids, msg, context)
            wf_service.trg_validate(uid, 'purchase.order', id, 'purchase_confirm', cr)
        return True

    def process_pickings(self, cr, uid, ids, pick_br, context):
        print "process_pickings"
        from stock.wizard import wizard_partial_picking
        for picking in pick_br:
            data = temp = {}
            moves = []
            for move in picking.move_lines:
                temp['move%s'% move.id] = move.product_qty
                if (picking.type == 'in') and (move.product_id.cost_method == 'average'):
                    price = 0
                    if hasattr(move, 'purchase_line_id') and move.purchase_line_id:
                        price = move.purchase_line_id.price_unit
                    currency = 0
                    if hasattr(picking, 'purchase_id') and picking.purchase_id:
                        currency = picking.purchase_id.pricelist_id.currency_id.id
                    temp['uom%s'% move.id] = move.product_uom.id
                    temp['price%s' % move.id] = price
                    temp['currency%s' % move.id] = currency
                moves.append(move.id)
            temp['moves'] = moves
            data['form'] = temp
            data['ids'] = [picking.id]
            data['report_type'] = 'pdf'
            data['model'] = 'stock.picking'
            data['id'] = picking.id
            wizard_partial_picking._do_split(self, cr, uid, data, context)
        return True

    def receive_deliver_products(self, cr, uid, ids, context):
        print "receive_deliver_products"
        picking_obj = self.pool.get('stock.picking')
        for type in ('in','out'):
            conf_pick = picking_obj.search(cr,uid,[('state','=','confirmed'),('type','=',type)])
            if len(conf_pick):
                picking_obj.force_assign(cr, uid, conf_pick, context)
            picking_ids = picking_obj.search(cr,uid,[('state','=','assigned'),('type','=',type)])
            pick_br = picking_obj.browse(cr,uid,picking_ids)
            self.process_pickings(cr, uid, ids, pick_br, context)
        return True

    def confirm_draft_invoices(self, cr, uid, ids, type, context):
        print "confirm_draft_invoices"
        try:
            wf_service = netsvc.LocalService('workflow')
            inv_obj = self.pool.get('account.invoice')
            draft_inv_id = inv_obj.search(cr,uid,[('state','=','draft'),('type','=',type)])
            for id in draft_inv_id:
                wf_service.trg_validate(uid, 'account.invoice', id, 'invoice_open', cr)
        except Exception, e:
            if type == 'out_invoice':
                msg = "There is a problem while confirming draft Customer invoices"
            else:
                msg = "There is a problem while confirming draft supplier invoices"
            self.update_messages(cr, uid, ids, msg, context)
        return True

    def pay_all_customer_invoice(self, cr, uid, ids, context):
        print "pay_all_customer_invoice"
        od = self.get_date(cr, uid,context)
        inv_obj = self.pool.get('account.invoice')
        journal = self.pool.get('account.journal').search(cr,uid,[('type','=','cash')])
        jour_br = self.pool.get('account.journal').browse(cr,uid,journal[0])
        if type(jour_br) == []:
            jour_br = jour_br[0]
        open_inv_id = inv_obj.search(cr,uid,[('state','=','open'),('type','=','out_invoice')])
        inv_br = inv_obj.browse(cr,uid,open_inv_id)
        for inv in inv_br:
            self._pay_and_reconcile(cr, uid, ids, inv.id, jour_br.id, inv.amount_total, od, context)
        return True

    def create_fiscalyear_and_period(self,cr, uid, ids, context={}, interval=1):
        print "create_fiscalyear_and_period"
        fys = self.pool.get('account.fiscalyear').search(cr, uid, [])
        if len(fys):
            new_fy = int(self.pool.get('account.fiscalyear').browse(cr, uid, fys[len(fys)-1]).code) + 1
        else:
            new_fy = int(time.strftime('%Y'))
        start_date = datetime.date(new_fy,1,1)
        stop_date = datetime.date(new_fy,12,31)
        fiscal_id = self.pool.get('account.fiscalyear').create(cr, uid,
                    {'name':'%d'%(new_fy),'code': '%d'%(new_fy),'date_start': start_date,
                    'date_stop': stop_date})
        self.pool.get('account.fiscalyear').create_period(cr, uid, [fiscal_id])
        return fiscal_id

    def close_fiscalyear(self, cr, uid, ids, close_fy, new_fy, context):
        print "close_fiscalyear"
        data = data1 = {}
        data['form'] = {}
        data1['form'] = {}
        opening_journal = self.pool.get('account.journal').search(cr, uid, [('code','ilike','JO')])[0]
        period_id = self.pool.get('account.period').search(cr, uid, [('fiscalyear_id', '=', new_fy)])[0]
        from account.wizard import wizard_fiscalyear_close,wizard_fiscalyear_close_state
        data['form']['period_id'] = period_id
        data['form']['report_name'] = 'End of Fiscal Year Entry'
        data['form']['journal_id'] = opening_journal
        data['form']['fy_id'] = close_fy
        data['form']['fy2_id'] = new_fy
        data['form']['sure'] = True
        data1['form']['fy_id'] = close_fy
        data1['form']['sure'] = True
        wizard_fiscalyear_close._data_save(self, cr, uid, data, context)
        wizard_fiscalyear_close_state._data_save(self, cr, uid, data1, context)
        return True

    def create_sale_periods(self, cr, uid, ids, context):
        print "create_sale_periods"
        period = self.pool.get('stock.period').search(cr, uid, [])
        if period or False:
            self.pool.get('stock.period').write(cr, uid, period[len(period)-1],{'state':'close'})
            period = int(self.pool.get('stock.period').browse(cr, uid, period[len(period)-1]).name) + 1
        else:
            period = int(time.strftime('%Y'))
        start_date = mx.DateTime.strptime(str(datetime.date(period,1,1)), '%Y-%m-%d')
        stop_date = mx.DateTime.strptime(str(datetime.date(period,12,31)), '%Y-%m-%d')
        sale_period_id = self.pool.get('stock.period').create(cr, uid, {
                'name': start_date.strftime('%Y'),
                'date_start': start_date.strftime('%Y-%m-%d'),
                'date_stop': stop_date.strftime('%Y-%m-%d'),
                'state':'open'
            })
        return True

    def create_sale_forecast_stock_planning_data(self, cr, uid, ids, syear, context):
        print "create_sale_forecast_stock_planning_data"
        user_id = self.pool.get('res.users').search(cr, uid, [('login','ilike','sale')])[0]
        period = self.pool.get('stock.period').search(cr, uid, [('name', '=', syear)])[0]
        prod_ids = self.pool.get('product.product').search(cr, uid, [])
        warehouse_id = self.pool.get('stock.warehouse').search(cr, uid, [])

        for product in self.pool.get('product.product').browse(cr, uid, prod_ids):
            self.pool.get('stock.planning.sale.prevision').create(cr, uid,{'user_id':user_id,
                                'period_id':period,'product_id':product.id,'product_qty':0.00,
                                'product_uom':product.product_tmpl_id.uom_id.id})
            if product.product_tmpl_id.procure_method == 'make_to_stock':
                self.pool.get('stock.planning').create(cr, uid,{'period_id':period,'product_id':product.id,
                    'planned_outgoing':0.0,'to_procure':0.0,'product_uom':product.product_tmpl_id.uom_id.id,
                    'warehouse_id':warehouse_id[0]})
        return True

    def procure_incomming_left(self, cr, uid, ids, cnt, context):
        print "procure_incomming_left"
        ids = self.pool.get('stock.planning').search(cr, uid, [])
        result = {}
        for obj in self.pool.get('stock.planning').browse(cr, uid, ids):
            location_id = obj.warehouse_id and obj.warehouse_id.lot_stock_id.id or False
            output_id = obj.warehouse_id and obj.warehouse_id.lot_output_id.id or False
            if location_id and output_id:
                move_id = self.pool.get('stock.move').create(cr, uid, {
                                'name': obj.product_id.name[:64],
                                'product_id': obj.product_id.id,
                                'date_planned': obj.period_id.date_start,
                                'product_qty': obj.incoming_left / 12,
                                'product_uom': obj.product_uom.id,
                                'product_uos_qty': obj.incoming_left / 12,
                                'product_uos': obj.product_uom.id,
                                'location_id': location_id,
                                'location_dest_id': output_id,
                                'state': 'waiting',
                            })
                proc_id = self.pool.get('mrp.procurement').create(cr, uid, {
                                'name': 'Procure left From Planning',
                                'origin': 'Stock Planning',
                                'date_planned': obj.period_id.date_start,
                                'product_id': obj.product_id.id,
                                'product_qty': obj.incoming_left / 12,
                                'product_uom': obj.product_uom.id,
                                'product_uos_qty': obj.incoming_left / 12,
                                'product_uos': obj.product_uom.id,
                                'location_id': obj.warehouse_id.lot_stock_id.id,
                                'procure_method': obj.product_id.product_tmpl_id.procure_method,
                                'move_id': move_id,
                            })
                wf_service = netsvc.LocalService("workflow")
                wf_service.trg_validate(uid, 'mrp.procurement', proc_id, 'button_confirm', cr)
                if cnt == 12:
                    self.pool.get('stock.planning').write(cr, uid, obj.id,{'state':'done'})
        return True

    def update_messages(self, cr, uid, ids, msg, context):
        print "update_messages"
        prev_msg = self.read(cr, uid, ids[0],['warn_error'])
        prev_msg['warn_error'] = prev_msg['warn_error'] or  ""
        prev_msg['warn_error']  += '\n' + '*' + msg
        self.write(cr, uid, ids[0],{'warn_error':prev_msg['warn_error']})
        return True

    def adjust_loan_account(self, cr, uid, ids, year, period, date, context):
         print "adjust_loan_account"
         acc_obj = self.pool.get('account.account')
         loan_obj = self.pool.get('bank.loan')
         loan_ids = loan_obj.search(cr, uid, [('months_left','>',0)])
         loans = loan_obj.browse(cr, uid, loan_ids)
         journal = self.pool.get('account.journal').search(cr,uid,[('type','=','cash')])[0]
         for loan in loans:
             move_id = self.pool.get('account.move').create(cr, uid,{'period_id':period,'journal_id':journal})
             loan_obj.write(cr, uid, loan.id,{'months_left':loan.months_left - 1})
             for code in ('512100','161000','661160'):
                    if code == '512100':
                        debit = 0.0
                        credit = loan.reimburse_principle_amt_with_int
                    if code == '161000':
                        debit = loan.reimburse_principle_amt_without_int
                        credit = 0.0
                    if code == '661160':
                        debit = loan.interest_per_month
                        credit = 0.0
                    acc_id = acc_obj.search(cr, uid, [('code','ilike',code)])[0]
                    self.pool.get('account.move.line').create(cr, uid, {'name' : 'Bank Loan','date':date,'account_id':acc_id,
                                        'credit':credit ,'debit': debit,'date_created':date,'move_id':move_id})
             self.pool.get('account.move').post(cr, uid, [move_id], context)
         return

    def get_traceback(self, cr, uid, ids, year, context):
        print "get_traceback"
        start_date = year.date_start
        stop_date = year.date_stop
        sale_order = purchase_order = cust_inv = supp_inv = goods_in = goods_out = 0
        sale_inv = pur_inv = nos = nop = nos_inv = noc_inv = 0
        models = {'sale.order':'sale.order.line','purchase.order':'purchase.order.line'}

        for model,model1 in models.items():
            orders = self.pool.get(model).search(cr, uid, [('date_order','<=',stop_date),('date_order','>=',start_date)])
            for order in orders:
                lines = self.pool.get(model1).search(cr, uid, [('order_id','=',order)])
                for line in self.pool.get(model1).browse(cr, uid, lines):
                    if model == 'sale.order':
                        nos = len(orders)
                        sale_order += line.product_uom_qty
                    else:
                        nop = len(orders)
                        purchase_order += line.product_qty

        for type in ('out_invoice','in_invoice'):
            total = 0.0
            total1 = 0.0
            inv_ids = self.pool.get('account.invoice').search(cr, uid, [('date_invoice','<=',stop_date),('date_invoice','>=',start_date),('type','ilike',type)])
            for inv in self.pool.get('account.invoice').browse(cr, uid, inv_ids):
                 total += inv.amount_total
                 for line in inv.invoice_line:
                     total1 += line.quantity
            if type == 'out_invoice':
                cust_inv = total
                sale_inv  = total1
                noc_inv = len(inv_ids)
            else:
                supp_inv = total
                pur_inv  = total1
                nos_inv = len(inv_ids)

        for type in ('in','out'):
            stock_ids = self.pool.get('stock.picking').search(cr, uid, [('date','<=',stop_date),('date','>=',start_date),('type','ilike',type)])
            for order in self.pool.get('stock.picking').browse(cr, uid, stock_ids):
                for moves in order.move_lines:
                    if type == 'in':
                        goods_in += moves.product_qty
                    else:
                        goods_out += moves.product_qty

        msg = ''' \t\tFiscal Year : %s
                ************************************
                 | Total Amount of Customer Invoices\t\t\t:  %s EUR
                 | Total Amount of Supplier Invoices\t\t\t:  %s EUR
                 | Total Incoming Goods\t\t\t\t\t\t:  %s Qty
                 | Total Outgoing Goods\t\t\t\t\t\t:  %s Qty
                 | Total [%s] Sale Orders Created with \t\t\t:  %s Qty of Products
                 | Total [%s] Purchase Orders Created with \t\t:  %s Qty of products
                 | Total [%s] Sale Orders Invoiced with \t\t\t:  %s Qty of products
                 | Total [%s] Purchase Orders Invoiced with \t\t:  %s Qty of products
                *************************************'''\
                %(year.code,cust_inv,supp_inv,goods_in,goods_out,nos,sale_order,nop,purchase_order,noc_inv,sale_inv,nos_inv,pur_inv)

        rec = self.browse(cr, uid, ids[0])
        full_ids = self.search(cr, uid, [])

        msg1 = ""
        if not rec.ay_traceback:
            if len(full_ids) == 1:
                full_ids = ids[0]
            else:
                full_ids = max(full_ids)-1
            rec1  = self.browse(cr, uid, full_ids)
            msg1 += '\n' + (rec1.ay_traceback or "")+ '\n' + msg
        else:
            msg1 += rec.ay_traceback + '\n' + msg
        self.write(cr, uid, ids[0],{'cy_traceback':msg,'ay_traceback':msg1})
        return

    def continue_next_year(self, cr, uid, ids, context):
        print "continue_next_year"
        fiscal_year_id = self.pool.get('account.fiscalyear').search(cr, uid, [('state','=','draft')])
        fy = self.pool.get('account.fiscalyear').browse(cr, uid, fiscal_year_id)[0]
        cr.execute("select id from res_partner")
        partner_ids = map(lambda x: x[0], cr.fetchall())
        cr.execute("select id from product_product")
        prod_ids = map(lambda x: x[0], cr.fetchall())
        cr.execute("select id from sale_shop")
        shop = map(lambda x: x[0], cr.fetchall())

        wf_service = netsvc.LocalService('workflow')
        cnt = 0
        for period in fy.period_ids:
            for i in range(0,random.randrange(1,10)):
                partner = random.randrange(len(partner_ids))
                partner_addr = self.pool.get('res.partner').address_get(cr, uid, [partner_ids[partner]],
                                ['invoice', 'delivery', 'contact'])
                pricelist = self.pool.get('res.partner').browse(cr, uid, partner_ids[partner],
                                context).property_product_pricelist.id
                fpos = self.pool.get('res.partner').browse(cr, uid, partner_ids[partner],
                                context).property_account_position
                fpos_id = fpos and fpos.id or False
                od = self.get_date(cr, uid, context)
                vals = {
                        'shop_id': shop[0],
                        'partner_id': partner_ids[partner],
                        'pricelist_id': pricelist,
                        'partner_invoice_id': partner_addr['invoice'],
                        'partner_order_id': partner_addr['contact'],
                        'partner_shipping_id': partner_addr['delivery'],
                        'order_policy': 'postpaid',
                        'date_order':od,
                        'fiscal_position': fpos_id
                    }
                new_id = self.pool.get('sale.order').create(cr, uid, vals)
                for j in range(0,random.randrange(1,5)):
                    product = random.randrange(len(prod_ids))
                    value = self.pool.get('sale.order.line').product_id_change(cr, uid, [], pricelist,
                                    prod_ids[product], qty=i, partner_id=partner_ids[partner], fiscal_position=fpos_id)['value']
                    value['product_id'] = prod_ids[product]
                    value['product_uom_qty'] = j + 100
                    value['order_id'] = new_id
                    self.pool.get('sale.order.line').create(cr, uid, value)
                wf_service.trg_validate(uid, 'sale.order', new_id, 'order_confirm', cr)
            cnt += 1
            print "period:::::::",period.code
            self.procure_incomming_left(cr, uid, ids, cnt, context)
            self.confirm_draft_po(cr, uid, ids, context)
            self.confirm_draft_invoices(cr, uid, ids, 'in_invoice', context)
            self.pay_supplier_invoice(cr, uid, ids, context)
            self.receive_deliver_products(cr, uid, ids, context)
            self.confirm_draft_invoices(cr, uid, ids, 'out_invoice', context)
            self.pay_all_customer_invoice(cr, uid, ids, context)
            self.adjust_loan_account(cr, uid, ids, fiscal_year_id, period.id, od, context)
            self.pool.get('account.period').write(cr, uid, period.id, {'state':'done'})
        self.get_traceback(cr, uid, ids, fy, context)
        self.create_sale_periods(cr, uid, ids, context)
        self.create_sale_forecast_stock_planning_data(cr, uid, ids, int(fy.code)+1, context)
        new_fy = self.create_fiscalyear_and_period(cr, uid, ids, context)
        self.close_fiscalyear(cr, uid, ids, fy.id, new_fy, context)
        return True

    def get_date(self, cr, uid,context):
        fp = self.pool.get('account.period').search(cr, uid, [('state', '=', 'draft')])[0]
        fp = self.pool.get('account.period').browse(cr, uid, fp)
        dstart = mx.DateTime.strptime(str(fp.date_start), '%Y-%m-%d')
        todate = 30
        if dstart.month == 2:
            todate = 28
        dt = datetime.date(dstart.year,dstart.month,random.randrange(1,todate))
        return dt

    def find(self, cr, uid, dt=None, context={}):
        dt = self.get_date(cr, uid,context)
        return super(account.period,self).find(cr, uid, dt, context)

profile_game_phase_two()

class mrp_production(osv.osv):
    _inherit = 'mrp.production'
    _columns = {}

    def create(self, cr, uid, vals, context={}):
         if self.pool.get('profile.game.phase1').check_state(cr, uid, context):
             vals ['date_planned'] = self.pool.get('profile.game.phase2').get_date(cr, uid,context)
         return super(mrp_production, self).create(cr, uid, vals, context)

mrp_production()

class mrp_procurement(osv.osv):
    _inherit = 'mrp.procurement'
    _columns = {}

    def create(self, cr, uid, vals, context={}):
        if self.pool.get('profile.game.phase1').check_state(cr, uid, context):
            vals ['date_planned'] = self.pool.get('profile.game.phase2').get_date(cr, uid,context)
        return super(mrp_procurement, self).create(cr, uid, vals, context)

mrp_procurement()

class stock_picking(osv.osv):
    _inherit = "stock.picking"
    _columns = {}

    def create(self, cr, uid, vals, context={}):
        if self.pool.get('profile.game.phase1').check_state(cr, uid, context):
          vals ['date'] = self.pool.get('profile.game.phase2').get_date(cr, uid,context)
        return super(stock_picking, self).create(cr, uid, vals, context)

stock_picking()

class stock_move(osv.osv):
     _inherit = "stock.move"
     _columns = {}

     def create(self, cr, uid, vals, context={}):
          if self.pool.get('profile.game.phase1').check_state(cr, uid, context):
              dt = self.pool.get('profile.game.phase2').get_date(cr, uid,context)
              vals ['date'] = dt
              vals['date_planned'] = dt
          return super(stock_move, self).create(cr, uid, vals, context)

stock_move()

class purchase_order(osv.osv):
     _inherit = "purchase.order"
     _columns = {}

     def create(self, cr, uid, vals, context={}):
          if self.pool.get('profile.game.phase1').check_state(cr, uid, context):
              vals ['date_order'] = self.pool.get('profile.game.phase2').get_date(cr, uid,context)
          return super(purchase_order, self).create(cr, uid, vals, context)

purchase_order()

class account_move_line(osv.osv):
    _inherit = "account.move.line"

    def _get_date(self, cr, uid, context):
        period_obj = self.pool.get('account.period')
        dt = self.pool.get('profile.game.phase2').get_date(cr, uid,context)
        if ('journal_id' in context) and ('period_id' in context):
            cr.execute('select date from account_move_line ' \
                    'where journal_id=%s and period_id=%s ' \
                    'order by id desc limit 1',
                    (context['journal_id'], context['period_id']))
            res = cr.fetchone()
            if res:
                dt = res[0]
            else:
                period = period_obj.browse(cr, uid, context['period_id'],
                        context=context)
                dt = period.date_start
        return dt


    def create(self, cr, uid, vals, context={}):
        if self.pool.get('profile.game.phase1').check_state(cr, uid, context):
            vals ['date'] = self._get_date(cr, uid, context)
            vals ['date_created'] = self.pool.get('profile.game.phase2').get_date(cr, uid,context)
        return super(account_move_line, self).create(cr, uid, vals, context)

    _columns = {}
account_move_line()

class account_invoice(osv.osv):
      _inherit = "account.invoice"
      _columns = {}


      def create(self, cr, uid, vals, context={}):
          if self.pool.get('profile.game.phase1').check_state(cr, uid, context):
              vals ['date_invoice'] = self.pool.get('profile.game.phase2').get_date(cr, uid,context)
          return super(account_invoice, self).create(cr, uid, vals, context)

account_invoice()