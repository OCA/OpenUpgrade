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
                'loan_duration' : fields.float('Number of Years', help="Loan duration in years"),
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
            }

bank_loan()

class profile_game_retail(osv.osv):
    _name="profile.game.retail"

    def fields_view_get(self, cr, uid, view_id=None, view_type='form', context={}, toolbar=False):
        res = super(profile_game_retail, self).fields_view_get(cr, uid, view_id, view_type, context=context, toolbar=toolbar)
        p_id = self.search(cr, uid, [])
        p_br = self.browse(cr, uid, p_id)
        for rec in p_br:
            if len(rec.sales_user_id.name):
                hr_name = " "
                if rec.hr_user_id:
                   hr_name = rec.hr_user_id.name
                res['arch'] = res['arch'].replace('SM', rec.sales_user_id.name)
                res['arch'] = res['arch'].replace('HRM',hr_name)
                res['arch'] = res['arch'].replace('FM',rec.finance_user_id.name)
                res['arch'] = res['arch'].replace('LM', rec.logistic_user_id.name)
                return res
        res['arch'] = res['arch'].replace('(SM)',"")
        res['arch'] = res['arch'].replace('(HR)',"")
        res['arch'] = res['arch'].replace('(FM)',"")
        res['arch'] = res['arch'].replace('(LM)',"")
        return res


    def _calculate_detail(self, cr, uid, ids, field_names, arg, context):
        res = {}
        fiscal_obj = self.pool.get('account.fiscalyear')
        account_obj = self.pool.get('account.account')
        account_type_obj = self.pool.get('account.account.type')
        fiscalyear_id = fiscal_obj.search(cr, uid, [('state','=','draft')])[0]
        fiscalyear = fiscal_obj.browse(cr,uid,fiscalyear_id)
        prev_fy = fiscal_obj.search(cr, uid, [('code','ilike', str(int(fiscalyear.code) - 1))])[0]
        prev_to_prev_fy = fiscal_obj.search(cr, uid, [('code','ilike', str(int(fiscalyear.code) - 2))])[0]
        print " field_names:::::::::::::::::::",field_names,ids

        for val in self.browse(cr, uid, ids, context=context):
            res[val.id] = {}
            if 'hr_budget' in field_names:
                res[val.id] = {}.fromkeys(field_names, 0.0)
            print "cur_year,prev_fy,prev_to_prev_fy",fiscalyear.id,prev_fy,prev_to_prev_fy

            # calculate finance detail
            total_reimburse = current_treasury = last_total_sale = sale_forcast = margin_forcast = last_turnover = 0.0
            total_sold_products = total_benefit = benefits_growth = turnover_growth = products_growth = cost_purchase_forcast = 0.0
            last_total_purchase = prev_to_prev_total_sale = prev_to_prev_prod_sold = prev_prod_sold = prev_to_prev_benefit = 0.0
            prev_to_prev_turnover = 0.0

            if 'total_reimburse' in field_names:
                account_ids = account_obj.search(cr,uid,[('user_type','ilike','payable')])
                context = {'fiscalyear': fiscalyear_id,'target_move':'all'}
                for acc in  account_obj.browse(cr, uid, account_ids, context):
                       total_reimburse += acc.balance
               # res[val.id]['total_reimburse'] = total_balance
                print "total_reimburse",total_reimburse

            if 'current_treasury' in field_names:
                cash_account_ids = account_obj.search(cr,uid,[('user_type','ilike','cash')])
                context = {'fiscalyear': fiscalyear_id,'target_move':'all'}
                for cash_account in account_obj.browse(cr, uid, cash_account_ids, context):
                    current_treasury += cash_account.balance
              #  res[val.id]['current_treasury'] = total_balance
                print "current_treasury",current_treasury
 # calculate sales detail

            if 'last_total_sale' in field_names:
                account_ids = account_obj.search(cr,uid,[('user_type','ilike','income')])
                total_balance = [0,0]
                i = 0
                for fy in (prev_fy,prev_to_prev_fy):
                    total_balance[i] = 0.0
                    context = {'fiscalyear': fy,'target_move':'all'}
                    for account in account_obj.browse(cr,uid,account_ids, context):
                        total_balance[i] += account.balance
                    i += 1
                #res[val.id]['last_total_sale'] = total_balance[0]
                last_total_sale = total_balance[0]
                prev_to_prev_total_sale = total_balance[1]
                print "last_total_sale",total_balance[0]
                print "prev_to_prev_total_sale",total_balance[1]

            if 'sale_forcast' in field_names:
                forecast_obj = self.pool.get('stock.planning.sale.prevision')
                forecast_ids = forecast_obj.search(cr, uid, [('period_id', '=',fiscalyear_id)])
                total_balance = 0.0
                for value in forecast_obj.browse(cr ,uid, forecast_ids):
                    sale_forcast += value.product_amt
               # res[val.id]['sale_forcast'] = total_balance
                print "sale_forcast",sale_forcast

            if 'margin_forcast' in field_names:
                forecast_obj = self.pool.get('stock.planning.sale.prevision')
                forecast_ids = forecast_obj.search(cr, uid, [('period_id', '=',fiscalyear_id)])
                for value in forecast_obj.browse(cr ,uid, forecast_ids):
                    margin_forcast += value.product_amt - (value.product_qty * value.product_id.standard_price)
              #  res[val.id]['margin_forcast'] = total_balance
                print "margin_forcast",margin_forcast
 # calculate Objectives Achievement
            if 'last_turnover' in field_names:
                 last_turnover = last_total_sale or 0.0
                 #res[val.id]['last_turnover'] =  last_total_sale or 0.0
                 prev_to_prev_turnover = prev_to_prev_total_sale or 0.0
                 print "last_turnover",last_total_sale or 0.0
                 print "prev_to_prev_turnover", prev_to_prev_total_sale  or 0.0

            if 'total_sold_products' in field_names:
                 total_balance = [0,0,0]
                 i = 0
                 for fy in fiscal_obj.browse(cr,uid,[fiscalyear_id, prev_fy,prev_to_prev_fy]):
                    sql="""
                        select
                        sum(invoice_line.quantity) as total
                        from account_invoice_line invoice_line
                        where invoice_line.invoice_id in (select id from account_invoice invoice
                        where invoice.type ='out_invoice' and date_invoice>='%s' and date_invoice<='%s')
                    """%(fy.date_start,fy.date_stop)
                    cr.execute(sql)
                    result = cr.fetchall()[0]
                    print "result",result
                    total_balance[i] = result[0] or 0.0
                    i += 1
                 total_sold_products =  total_balance[0]
              #   res[val.id]['total_sold_products'] = total_balance[0]
                 prev_prod_sold = total_balance[1]
                 prev_to_prev_prod_sold = total_balance[2]
                 print "total_sold_products", total_balance[0]
                 print "prev_prod_sold", total_balance[1]
                 print "prev_to_prev_prod_sold", total_balance[2]

            if 'total_benefit' in field_names:
                total_balance = [0,0]
                prev_to_prev_benefit = 0.0
                account_ids = account_obj.search(cr,uid,[('user_type','ilike','expense')])
                for fy in (prev_fy,prev_to_prev_fy):
                    i = 0
                    total_balance[i] = 0.0
                    context = {'fiscalyear': fy,'target_move':'all'}
                    for account in account_obj.browse(cr,uid,account_ids, context):
                        total_balance[i] += account.balance
                total_benefit = last_turnover or 0.0 - total_balance[0] or 0.0
                #res[val.id]['total_benefit'] = val.last_turnover or 0.0 - total_balance[0] or 0.0
                prev_to_prev_benefit = prev_to_prev_turnover or 0.0 - total_balance[1] or 0.0
                print "total_benefit", total_benefit or 0.0
                print "prev_to_prev_benefit", prev_to_prev_benefit or 0.0

            if 'benefits_growth' in field_names:
                benefits_growth = total_benefit or 0.0 - prev_to_prev_benefit or 0.0
                #res[val.id]['benefits_growth'] = val.total_benefit or 0.0 - prev_to_prev_benefit or 0.0
                print "benefits_growth", benefits_growth

            if 'turnover_growth' in field_names:
                turnover_growth = last_turnover or 0.0 - prev_to_prev_turnover or 0.0
                #res[val.id]['turnover_growth'] = val.last_turnover or 0.0 - prev_to_prev_turnover or 0.0
                print "turnover_growth", res[val.id]['turnover_growth'] or 0.0

            if 'products_growth' in field_names:
                products_growth = prev_prod_sold or 0.0- prev_to_prev_prod_sold or 0.0
               # res[val.id]['products_growth'] = prev_prod_sold or 0.0- prev_to_prev_prod_sold or 0.0
                print "products_growth", res[val.id]['products_growth'] or 0.0

            if 'cost_purchase_forcast' in field_names:
                sum1 = 0.0
                sum2 = 0.0
                period_id = self.pool.get('stock.period').search(cr, uid, [('name','ilike', fiscalyear.code)])
                stock_ids = self.pool.get('stock.planning').search(cr, uid, [('period_id','in', period_id)])
                forecast_ids = self.pool.get('stock.planning.sale.prevision').search(cr, uid, [('period_id','in', period_id)])
                for stock in self.pool.get('stock.planning').browse(cr, uid,stock_ids):
                    sum1 += stock.incoming_left * stock.product_id.standard_price
                for forecast in self.pool.get('stock.planning.sale.prevision').browse(cr, uid, forecast_ids):
                    sum2 += forecast.product_qty * forecast.product_id.standard_price
               # res[val.id]['cost_purchase_forcast'] = sum1 + sum2
                cost_purchase_forcast = sum1 + sum2
                print "cost_purchase_forcast", sum1 + sum2

            if 'last_total_purchase' in field_names:
                    fy = fiscal_obj.browse(cr,uid,prev_fy)
                    sql="""
                        select
                        sum(invoice_line.quantity) as total
                        from account_invoice_line invoice_line
                        where invoice_line.invoice_id in (select id from account_invoice invoice
                        where invoice.type ='in_invoice' and date_invoice>='%s' and date_invoice<='%s')
                        """%(fy.date_start,fy.date_stop)
                    cr.execute(sql)
                    result = cr.fetchall()[0]
                    last_total_purchase =  result[0] or 0.0
                    #res[val.id]['last_total_purchase'] = result[0] or 0.0
                    print "last_total_purchase", result[0]

            for field in field_names:
                if field == 'total_reimburse':
                    res[val.id][field] = total_reimburse

                elif field == 'current_treasury':
                    res[val.id][field] = current_treasury

                elif field == 'last_total_sale':
                    res[val.id][field] = last_total_sale

                elif field == 'sale_forcast':
                        res[val.id][field] = sale_forcast

                elif field == 'margin_forcast':
                        res[val.id][field] = margin_forcast

                elif field == 'last_turnover':
                        res[val.id][field] = last_turnover

                elif field == 'total_sold_products':
                        res[val.id][field] = total_sold_products
                elif field == 'total_benefit':
                        res[val.id][field] = total_benefit
                elif field == 'benefits_growth':
                        res[val.id][field] = benefits_growth
                elif field == 'turnover_growth':
                        res[val.id][field] = turnover_growth
                elif field == 'products_growth':
                        res[val.id][field] = products_growth

                elif field == 'cost_purchase_forcast':
                        res[val.id][field] = cost_purchase_forcast
                elif field == 'last_total_purchase':
                        res[val.id][field] = last_total_purchase
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
       # 'expenses_forecast' : fields.function(_calculate_detail, method=True, type='float', string='Expenses Forecast', multi='finance',help="Sum of all budgets of the year"),
        'current_treasury' : fields.function(_calculate_detail, method=True, type='float', string='Current treasury', multi='finance',help="Balance of all Cash Accounts"),
        'total_reimburse' : fields.function(_calculate_detail, method=True, type='float', string='Total to Reimburse', multi='finance',help="Total to Reimburse"),
       # 'total_current_refund' : fields.function(_calculate_detail, method=True, type='float', string='To Reimburse this Year', multi='finance',help="To Reimburse this Year"),
        'loan_total_reimburse' : fields.float('Total to Reimburse', readonly=True, help="Total loan amount to reimburse "),
        'loan_total_reimburse_this_year' : fields.float('Total to Reimburse this year', readonly=True, help="Total loan amount to reimburse this year"),

        'hr_budget' : fields.function(_calculate_detail, method=True, type='float', string='HR Budget', multi='finance',help="HR Budget"),

        'last_total_sale' : fields.function(_calculate_detail, method=True, type='float', string='Total Sales in Last Year', multi='finance',help="Total Sales in Last Year"),
        'sale_forcast' : fields.function(_calculate_detail, method=True, type='float', string='Sales Forcast', multi='finance',help="Sales Forcast"),
        'margin_forcast' : fields.function(_calculate_detail, method=True, type='float', string='Margin Forcast', multi='finance',help="Margin Forcast"),

        'last_total_purchase' : fields.function(_calculate_detail, method=True, type='float', string='Total Purchases in Last year', multi='finance',help="Total Purchases in Last year"),
        'avg_stock_forcast' : fields.function(_calculate_detail, method=True, type='float', string='Avg. Stock Forcast', multi='finance',help="Avg. Stock Forcast"),
        'cost_purchase_forcast' : fields.function(_calculate_detail, method=True, type='float', string='Costs of Purchases Forecast', multi='finance',help="Costs of Purchases Forecast"),

        'last_turnover' : fields.function(_calculate_detail, method=True, type='float', string='Turnover in last year', multi='finance',help="Turnover in last year"),
        'total_benefit' : fields.function(_calculate_detail, method=True, type='float', string='Total Benefits', multi='finance',help="Total Benefits"),
        'total_sold_products' : fields.function(_calculate_detail, method=True, type='float', string='# of Products Sold', multi='finance',help="# of Products Sold"),
        'turnover_growth' : fields.function(_calculate_detail, method=True, type='float', string='Turnover Growth', multi='finance',help="Turnover Growth"),
        'benefits_growth' : fields.function(_calculate_detail, method=True, type='float', string='Benefits Growth', multi='finance',help="Benefits Growth"),
        'products_growth' : fields.function(_calculate_detail, method=True, type='float', string='Growth Products', multi='finance',help="Growth Products"),
        'cy_traceback':fields.text('Traceback [Current Year]'),
        'warn_error':fields.text('Warnings & Errors'),
        'ay_traceback':fields.text('Traceback [All Years]'),
    }
    _defaults = {
        'cy_traceback' : lambda *a : "",
        'warn_error' : lambda *a : "",
        'ay_traceback' : lambda *a : ""
          }


    def pay_supplier_invoice(self, cr, uid, ids, context):
        od = self.get_date(cr, uid,context)
        print "pay_supplier_invoice"
     #   try:
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
       # except Exception, e:
            #  self.update_messages(cr, uid, ids, e, context)
        return True

    def _pay_and_reconcile(self, cr, uid, ids, invoice_id, journal_id, amount, od, context):
      #   try:
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

        # except Exception, e:
         #    self.update_messages(cr, uid, ids, e, context)
        return True

    def confirm_draft_supplier_invoice(self, cr, uid, ids, context):
        print "confirm_draft_supplier_invoice"
        try:
            wf_service = netsvc.LocalService('workflow')
            inv_obj = self.pool.get('account.invoice')
            draft_inv_id = inv_obj.search(cr,uid,[('state','=','draft'),('type','=','in_invoice')])
            for id in draft_inv_id:
                wf_service.trg_validate(uid, 'account.invoice', id, 'invoice_open', cr)
        except Exception, e:
             msg = "There is a problem while confirming draft supplier invoices"
             self.update_messages(cr, uid, ids, msg, context)
        return True

    def confirm_draft_po(self, cr, uid, ids, context):
        print "confirm_draft_po"
       # try:
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
        #except Exception, e:
         #    self.update_messages(cr, uid, ids, e, context)
        return True

    def process_pickings(self, cr, uid, ids, pick_br, context):
        print "process_pickings"
       # try:
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
       # except Exception, e:
           #  self.update_messages(cr, uid, ids, e, context)
        return True

    def receive_products(self, cr, uid, ids, context):
        print "receive_products"
       # try:
        picking_obj = self.pool.get('stock.picking')
        conf_pick = picking_obj.search(cr,uid,[('state','=','confirmed'),('type','=','in')])
        if len(conf_pick):
            picking_obj.force_assign(cr, uid, conf_pick, context)
        picking_ids = picking_obj.search(cr,uid,[('state','=','assigned'),('type','=','in')])
        pick_br = picking_obj.browse(cr,uid,picking_ids)
        self.process_pickings(cr, uid, ids, pick_br, context)
       # except Exception, e:
        #     self.update_messages(cr, uid, ids, e, context)
        return True

    def deliver_products(self, cr, uid, ids, context):
        print "deliver_products"
       # try:
        picking_obj = self.pool.get('stock.picking')
        conf_pick = picking_obj.search(cr,uid,[('state','=','confirmed'),('type','=','out')])
        if len(conf_pick):
            picking_obj.force_assign(cr, uid, conf_pick, context)
        picking_ids = picking_obj.search(cr,uid,[('state','=','assigned'),('type','=','out')])
        pick_br = picking_obj.browse(cr,uid,picking_ids)
        self.process_pickings(cr, uid, ids, pick_br, context)
       # except Exception, e:
       #      self.update_messages(cr, uid, ids, e, context)
        return True

    def confirm_draft_customer_invoice(self, cr, uid, ids, context):
        print "confirm_draft_customer_invoice"
        try:
            wf_service = netsvc.LocalService('workflow')
            inv_obj = self.pool.get('account.invoice')
            draft_inv_id = inv_obj.search(cr,uid,[('state','=','draft'),('type','=','out_invoice')])
            for id in draft_inv_id:
                wf_service.trg_validate(uid, 'account.invoice', id, 'invoice_open', cr)
        except Exception, e:
            msg = "There is a problem while confirming draft supplier invoices"
            self.update_messages(cr, uid, ids, msg, context)
        return True

    def pay_all_customer_invoice(self, cr, uid, ids, context):
        od = self.get_date(cr, uid,context)
        print "pay_all_customer_invoice"
        #try:
        inv_obj = self.pool.get('account.invoice')
        journal = self.pool.get('account.journal').search(cr,uid,[('type','=','cash')])
        jour_br = self.pool.get('account.journal').browse(cr,uid,journal[0])
        if type(jour_br) == []:
            jour_br = jour_br[0]
        open_inv_id = inv_obj.search(cr,uid,[('state','=','open'),('type','=','out_invoice')])
        inv_br = inv_obj.browse(cr,uid,open_inv_id)
        for inv in inv_br:
            maturity_date = inv.move_id.line_id[0].date_maturity
           # if (not maturity_date) or (maturity_date  <= now()):
            self._pay_and_reconcile(cr, uid, ids, inv.id, jour_br.id, inv.amount_total, od, context)
       # except Exception, e:
            # self.update_messages(cr, uid, ids, e, context)
        return True

    def create_fiscalyear_and_period(self,cr, uid, ids, context={}, interval=1):
        print "create_fiscalyear_and_period"
       # try:
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

        ds = mx.DateTime.strptime(str(start_date), '%Y-%m-%d')
        while ds.strftime('%Y-%m-%d')< str(stop_date):
            de = ds + RelativeDateTime(months=interval, days=-1)
            if de.strftime('%Y-%m-%d')>str(stop_date):
                de=mx.DateTime.strptime(stop_date, '%Y-%m-%d')

            self.pool.get('account.period').create(cr, uid, {
                'name': ds.strftime('%m/%Y'),
                'code': ds.strftime('%m/%Y'),
                'date_start': ds.strftime('%Y-%m-%d'),
                'date_stop': de.strftime('%Y-%m-%d'),
                'fiscalyear_id': fiscal_id,
            })
            ds = ds + RelativeDateTime(months=interval)
        #except Exception, e:
          #   self.update_messages(cr, uid, ids, e, context)
        return fiscal_id

    def close_fiscalyear(self, cr, uid, ids, fy, context):
        print "close_fiscalyear"
       # try:
        id = self.pool.get('account.fiscalyear').search(cr, uid, [('code','=',fy.code)])
        self.pool.get('account.fiscalyear').write(cr, uid, id,{'state':'done'})
      #  except Exception, e:
        #     self.update_messages(cr, uid, ids, e, context)
        return True

    def create_sale_periods(self, cr, uid, ids, context):
        print "create_sale_periods"
        #try:
        period = self.pool.get('stock.period').search(cr, uid, [])
        self.pool.get('stock.period').write(cr, uid, period[len(period)-1],{'state':'close'})
        period = int(self.pool.get('stock.period').browse(cr, uid, period[len(period)-1]).name) + 1
        start_date = mx.DateTime.strptime(str(datetime.date(period,1,1)), '%Y-%m-%d')
        stop_date = mx.DateTime.strptime(str(datetime.date(period,12,31)), '%Y-%m-%d')
        sale_period_id = self.pool.get('stock.period').create(cr, uid, {
                'name': start_date.strftime('%Y'),
                'date_start': start_date.strftime('%Y-%m-%d'),
                'date_stop': stop_date.strftime('%Y-%m-%d'),
                'state':'open'
            })
       # except Exception, e:
         #    self.update_messages(cr, uid, ids, e, context)
        return True

    def create_sale_forecast_stock_planning_data(self, cr, uid, ids, syear, context):
        print "create_sale_forecast_stock_planning_data"

        #try:
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
       # except Exception, e:
       #      self.update_messages(cr, uid, ids, e, context)
        return True

    def procure_incomming_left(self, cr, uid, ids, cnt, context):
        print "procure_incomming_left"
        #try:
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
                                'product_qty': obj.stock_incoming_left / 12,
                                'product_uom': obj.product_uom.id,
                                'product_uos_qty': obj.stock_incoming_left / 12,
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
                                'product_qty': obj.stock_incoming_left / 12,
                                'product_uom': obj.product_uom.id,
                                'product_uos_qty': obj.stock_incoming_left / 12,
                                'product_uos': obj.product_uom.id,
                                'location_id': obj.warehouse_id.lot_stock_id.id,
                                'procure_method': obj.product_id.product_tmpl_id.procure_method,
                                'move_id': move_id,
                            })
                wf_service = netsvc.LocalService("workflow")
                wf_service.trg_validate(uid, 'mrp.procurement', proc_id, 'button_confirm', cr)
                if cnt == 12:
                    self.pool.get('stock.planning').write(cr, uid, obj.id,{'state':'done'})
       # except Exception, e:
         #    self.update_messages(cr, uid, ids, e, context)
        return True

    def update_messages(self, cr, uid, ids, msg, context):
        print "update_messages"
        try:
            prev_msg = self.read(cr, uid, ids[0],['warn_error'])
            if prev_msg['warn_error'] == False:
              prev_msg['warn_error'] = '\n' + '*' + msg
            else:
                prev_msg['warn_error'] += '\n' + '*' + msg
            self.write(cr, uid, ids[0],{'warn_error':prev_msg['warn_error']})
        except Exception, e:
            print "There was an Exception"
            pass
        return True

    def continue_next_year(self, cr, uid, ids, context):
        fiscal_year_id = self.pool.get('account.fiscalyear').search(cr, uid, [('state','=','draft')])
        fy = self.pool.get('account.fiscalyear').browse(cr, uid, fiscal_year_id)[0]
        self.create_sale_periods(cr, uid, ids, context)
        self.create_sale_forecast_stock_planning_data(cr, uid, ids, fy.code, context)

        partner_ids = self.pool.get('res.partner').search(cr,uid,[])
        prod_ids = self.pool.get('product.product').search(cr,uid,[])
        shop = self.pool.get('sale.shop').search(cr,uid,[])
        wf_service = netsvc.LocalService('workflow')
        cnt = 0
        print "FYYYYYYYYYY",fy.code
        ## Create Random number of sale orders ##
        for period in fy.period_ids:
            for i in range(1,random.randrange(1,10)):
                partner = random.randrange(len(partner_ids))
                partner_addr = self.pool.get('res.partner').address_get(cr, uid, [partner_ids[partner]],
                                ['invoice', 'delivery', 'contact'])
                pricelist = self.pool.get('res.partner').browse(cr, uid, partner_ids[partner],
                                context).property_product_pricelist.id
                dstart = mx.DateTime.strptime(str(period.date_start), '%Y-%m-%d')
                dstop =  mx.DateTime.strptime(str(period.date_stop), '%Y-%m-%d')
                order_date = datetime.date(dstart.year,dstart.month,random.randrange(1,dstop.day + 1))
                od = (mx.DateTime.strptime(str(order_date), '%Y-%m-%d')).strftime('%Y-%m-%d')
                vals = {
                        'shop_id': shop[0],
                        'partner_id': partner_ids[partner],
                        'pricelist_id': pricelist,
                        'partner_invoice_id': partner_addr['invoice'],
                        'partner_order_id': partner_addr['contact'],
                        'partner_shipping_id': partner_addr['delivery'],
                        'order_policy': 'postpaid',
                        'date_order':od
                    }
                new_id = self.pool.get('sale.order').create(cr, uid, vals)

                for j in range(1,random.randrange(1,5)):
                    product = random.randrange(len(prod_ids))
                    value = self.pool.get('sale.order.line').product_id_change(cr, uid, [], pricelist,
                                    prod_ids[product], qty=i, partner_id=partner_ids[partner])['value']
                    value['product_id'] = prod_ids[product]
                    value['product_uom_qty'] = j + 100
                    value['order_id'] = new_id
                    self.pool.get('sale.order.line').create(cr, uid, value)
                wf_service.trg_validate(uid, 'sale.order', new_id, 'order_confirm', cr)
            cnt += 1
            self.procure_incomming_left(cr, uid, ids, cnt, context)
            self.confirm_draft_po(cr, uid, ids, context)
            self.confirm_draft_supplier_invoice(cr, uid, ids, context)
            self.pay_supplier_invoice(cr, uid, ids, context)
            self.receive_products(cr, uid, ids, context)
            self.deliver_products(cr, uid, ids, context)
            self.confirm_draft_customer_invoice(cr, uid, ids, context)
            self.pay_all_customer_invoice(cr, uid, ids, context)
            self.pool.get('account.period').write(cr, uid, period.id, {'state':'done'})
        self.close_fiscalyear(cr, uid, ids, fy, context)
        self.create_fiscalyear_and_period(cr, uid, ids, context)
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

profile_game_retail()

class profile_game_config_wizard(osv.osv_memory):
    _name='profile.game.config.wizard'
    _columns = {
        'state':fields.selection([('3','3'),('4','4')],'Number of Players',required=True),
        'finance_name':fields.char('Name of Financial Manager',size='64', required=True),
        'finance_email':fields.char('Email of Financial Manager',size='64'),
        'hr_name':fields.char('Name of Hurman Ressources Manager',size='64', readonly=True,required=False,states={'4':[('readonly',False),('required',True)]}),
        'hr_email':fields.char('Email of Hurman Ressources Manager',size='64',readonly=True,required=False,states={'4':[('readonly',False),('required',False)]}),
        'logistic_name':fields.char('Name of Logistic Manager',size='64', required=True),
        'logistic_email':fields.char('Email of Logistic Manager',size='64'),
        'sale_name':fields.char('Name of Sales Manager',size='64', required=True),
        'sale_email':fields.char('Email of Sales Manager',size='64'),
        'objectives':fields.selection([
            ('on_max_turnover','Maximise Turnover of Last Year'),
            ('on_max_cumulative','Maximise Cumulative Benefit'),
            ('on_max_products_sold','Maximise Number of Products Sold')],'Objectives',required=True),
        'years':fields.selection([
            ('3','3 Years (40 minutes)'),
            ('5','5 Years (1 hour)'),
            ('7','7 Years (1 hours and 20 minutes)')],'Number of Turns',required=True),
        'difficulty':fields.selection([
            ('easy','Easy'),
            ('medium','Medium'),
            ('hard','Hard')],'Difficulty',required=True),
    }
    _defaults = {
        'difficulty': lambda *args: 'medium',
        'years': lambda *args: '5',
        'objectives': lambda *args: 'on_max_turnover',
        'state': lambda *args: '3',
    }

#    def action_cancel(self, cr, uid, ids, conect = None):
#
#        return {
#            'view_type': 'form',
#            "view_mode": 'form',
#            'res_model': 'ir.actions.configuration.wizard',
#            'type': 'ir.actions.act_window',
#            'target':'new',
#        }

    def action_run(self, cr, uid, ids, context = None):
        game_obj = self.pool.get('profile.game.retail')
        fiscal_obj = self.pool.get('account.fiscalyear')
        user_obj = self.pool.get('res.users')
        emp_obj = self.pool.get('hr.employee')
        for res in self.read(cr, uid, ids, context = context):
            if res.get('id',False):
                del res['id']
            game_vals = {
                'state':res['state'],
                'objectives':res['objectives'],
                'years':res['years'],
                'difficulty':res['difficulty'],
            }
            game_id = game_obj.create(cr,uid,game_vals,context=context)
            lower = -2
            years = int(res['years'])
            players = int(res['state'])
            start_date = mx.DateTime.strptime(time.strftime('%Y-01-01'),'%Y-%m-%d')
            stop_date = mx.DateTime.strptime(time.strftime('%Y-12-31'),'%Y-%m-%d')
            while lower <= years:
                new_start_date = datetime.date(start_date.year+lower,1,1)
                new_stop_date = datetime.date(stop_date.year+lower,12,31)
                name = new_start_date.strftime('%Y')
                vals = {
                    'name':name,
                    'code':name,
                    'date_start':new_start_date,
                    'date_stop':new_stop_date,
                }
                new_id = fiscal_obj.create(cr, uid, vals, context=context)
                fiscal_obj.create_period3(cr, uid, [new_id])
                lower += 1
            for user_name in ['finance','sale','logistic','hr']:
                if user_name == 'hr' and players < 4:
                    continue
                user_ids = user_obj.name_search(cr, uid, user_name)
                user_id = len(user_ids) and user_ids[0][0] or False
                if user_name == 'finance':
                    game_vals['finance_user_id'] = user_id
                if user_name == 'sale':
                    game_vals['sales_user_id'] = user_id
                if user_name == 'logistic':
                    game_vals['logistic_user_id'] = user_id
                if user_name == 'hr':
                    game_vals['hr_user_id'] = user_id
                game_obj.write(cr, uid, game_id, game_vals)
                name = res.get(user_name+'_name','')
                if name:
                    email = res.get(user_name+'_email','')
                    emp_ids = emp_obj.search(cr,uid,[('user_id','=',user_id)])
                    if not len(emp_ids):
                        emp_obj.create(cr,uid,{
                                'name':name.strip(),
                                'work_email':email
                        })
                    else:
                        emp_obj.write(cr,uid,emp_ids,{
                                'name':name.strip(),
                                'work_email':email
                        })
                    user_obj.write(cr,uid,[user_id],{'name':name.strip()})
        return {
                'view_type': 'form',
                "view_mode": 'form',
                'res_model': 'ir.actions.configuration.wizard',
                'type': 'ir.actions.act_window',
                'target':'new',
            }
profile_game_config_wizard()

class mrp_production(osv.osv):
    _inherit = 'mrp.production'
    _columns = {}

    def create(self, cr, uid, vals, context={}):
         if self.pool.get('profile.game.retail.phase1').check_state(cr, uid, context):
             vals ['date_planned'] = self.pool.get('profile.game.retail').get_date(cr, uid,context)
         return super(mrp_production, self).create(cr, uid, vals, context)

mrp_production()

class mrp_procurement(osv.osv):
    _inherit = 'mrp.procurement'
    _columns = {}

    def create(self, cr, uid, vals, context={}):
        if self.pool.get('profile.game.retail.phase1').check_state(cr, uid, context):
            vals ['date_planned'] = self.pool.get('profile.game.retail').get_date(cr, uid,context)
        return super(mrp_procurement, self).create(cr, uid, vals, context)

mrp_procurement()

class stock_picking(osv.osv):
    _inherit = "stock.picking"
    _columns = {}

    def create(self, cr, uid, vals, context={}):
        if self.pool.get('profile.game.retail.phase1').check_state(cr, uid, context):
          vals ['date'] = self.pool.get('profile.game.retail').get_date(cr, uid,context)
        return super(stock_picking, self).create(cr, uid, vals, context)

stock_picking()

class stock_move(osv.osv):
     _inherit = "stock.move"
     _columns = {}

     def create(self, cr, uid, vals, context={}):
          if self.pool.get('profile.game.retail.phase1').check_state(cr, uid, context):
              vals ['date'] = self.pool.get('profile.game.retail').get_date(cr, uid,context)
          return super(stock_move, self).create(cr, uid, vals, context)

stock_move()

class purchase_order(osv.osv):
     _inherit = "purchase.order"
     _columns = {}

     def create(self, cr, uid, vals, context={}):
          if self.pool.get('profile.game.retail.phase1').check_state(cr, uid, context):
              vals ['date_order'] = self.pool.get('profile.game.retail').get_date(cr, uid,context)
          return super(purchase_order, self).create(cr, uid, vals, context)

purchase_order()

#class account_move(osv.osv):
#    _inherit = "account.move"
#    _columns = {}
#    _defaults = {
#        'period_id': _get_period,
#        }
#account_move()

class account_move_line(osv.osv):
    _inherit = "account.move.line"

    def _get_date(self, cr, uid, context):
        period_obj = self.pool.get('account.period')
        dt = self.pool.get('profile.game.retail').get_date(cr, uid,context)
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
        if self.pool.get('profile.game.retail.phase1').check_state(cr, uid, context):
            vals ['date'] = self._get_date(cr, uid, context)
            vals ['date_created'] = self.pool.get('profile.game.retail').get_date(cr, uid,context)
        return super(account_move_line, self).create(cr, uid, vals, context)

    _columns = {}
account_move_line()

class account_invoice(osv.osv):
      _inherit = "account.invoice"
      _columns = {}


      def create(self, cr, uid, vals, context={}):
          if self.pool.get('profile.game.retail.phase1').check_state(cr, uid, context):
              vals ['date_invoice'] = self.pool.get('profile.game.retail').get_date(cr, uid,context)
          return super(account_invoice, self).create(cr, uid, vals, context)

account_invoice()