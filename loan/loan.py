#!/usr/bin/env python
#-*- coding:utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution    
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>). All Rights Reserved
#    d$
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
import pooler
from osv import osv
from osv import fields
from datetime import date

class loan_customer(osv.osv):
    _name = 'res.partner'
    _inherit = 'res.partner'
    _columns = {
        'incom': fields.float('Monthly Incom',digits=(12,3)),
    }
loan_customer()

class loan_partner_bank(osv.osv):
    _name = 'res.partner.bank'
    _inherit = 'res.partner.bank'
    _columns = {
        'account_id': fields.many2one('account.account','Account'),
    }
loan_partner_bank()

class account_loan(osv.osv):

    def _loan_period_get(self, cr, uid, context={}):
        obj = self.pool.get('loan.installment.period')
        ids = obj.search(cr, uid,[('name','ilike','')])
        res = obj.read(cr, uid, ids, ['name','period'], context)
        return [(r['name'], r['name']) for r in res]

    def _loan_type_get(self, cr, uid, context={}):
        obj = self.pool.get('account.loan.loantype')
        ids = obj.search(cr, uid,[('name','ilike','')])
        res = obj.read(cr, uid, ids, ['name','calculation'], context)
        return [(r['name'], r['name']) for r in res]

    def cal_amt(self,cr,uid,ids,vals,context={}):      
        read_obj = self.read(cr,uid,ids)
        for read_id in read_obj:
            amt = read_id['loan_amt']
            mth = read_id['month']
            int = read_id['int_rate'] 
            k = 12
            i = int/100
            a = i/k or 0.00
            b = (1 - (1/((1+(i/k))**mth))) or 0.00
            emi = ( ( amt * a ) / b ) or 0.00
            tot_amt = emi * mth
            tot_int_amt = tot_amt - amt
            yr_amt = ( tot_int_amt * k ) / mth
            flat_pa = ( yr_amt * 100 ) / amt
            flat_pm = flat_pa / k
            
        self.write(cr,uid,ids,{'emi_cal':emi,'tot_amt':tot_amt,'flat_pa':flat_pa,'flat_pm':flat_pm,'tot_int_amt':tot_int_amt,'yr_int_amt':yr_amt})                               
        return True     
 
    def re_set(self,cr,uid,ids,vals,context={}):          
        self.write(cr,uid,ids,{'loan_amt':0.00,'month':0,'int_rate':0.00,'emi_cal':0.00,'tot_amt':0.00,'flat_pa':0.00,'flat_pm':0.00,'tot_int_amt':0.00,'yr_int_amt':0.00})                               
        return True   

    _name = 'account.loan'
    _columns = {
        'id': fields.integer('ID', readonly=True),
        'loan_id': fields.char('Loan Id', size=32, required=True),
        'proof_id':fields.one2many('account.loan.proof','loan_id','Proof Detail'),
        'auto_id': fields.integer('Auto Id', size=32),
        'name': fields.char('Description', size=128, required=True),
        'partner_id': fields.many2one('res.partner', 'Customer'),
        'proof_1': fields.many2one('res.partner', 'Gaurenter 1'),
        'proof_2': fields.many2one('res.partner', 'Gaurenter 2'),
        'contact': fields.many2one('res.partner.address', 'Contact'),
        'loan_type':fields.selection(_loan_type_get,'Loan Type', size=32 ,select=True, required=True),
        'loan_period':fields.selection(_loan_period_get,'Loan Period',select=True, required=True),
        'loan_amount': fields.float('Loan Amount',digits=(12,2), states={'draft':[('readonly',False)]}),
        'approve_amount': fields.float('Approve Amount',digits=(12,2),readonly=True),
        'process_fee': fields.float('Processing Fee',digits=(12,2)),
        'total_installment': fields.integer('Total Installment', readonly=False),
        'interest_rate': fields.float('Interest Rate',digits=(10,2),readonly=True),
        'apply_date': fields.date('Apply Date', states={'draft':[('readonly',False)]}),
        'approve_date': fields.date('Approve Date',readonly=True),
        'cheque_ids':fields.one2many('account.loan.bank.cheque','loan_id','Cheque Detail'),
        'state': fields.selection([
           ('draft','Quotation'),
           ('proof approval','Proof Approved'),
           ('apply','Applied'),
           ('approved','Approved'),
           ('done','Done'),
           ('cancel','Reject'),
        ],'State', readonly=True, select=True),
        'return_type': fields.selection([
           ('cash','By Cash'),
           ('cheque','By Cheque'),
           ('automatic','Automatic Payment'),
        ],'Payment Type', select=True),
        'pricelist_id': fields.many2one('product.pricelist', 'Pricelist', required=False, readonly=True, states={'draft':[('readonly',False)]}),
        'running_loan' : fields.many2many('account.loan', 'account_loan_running','loan_id','auto_id', 'Current Loans'),
        'installment_id' :fields.one2many('account.loan.installment','loan_id','Installments'),
        'interest' : fields.float('Interest'),
        'voucher_id': fields.many2one('account.voucher', 'Voucher',readonly=True),
        'notes' : fields.text('Description'),
        'cus_pay_acc': fields.property(
                'account.account',
                type='many2one',
                relation='account.account',
                string="Customer Loan Account",
                method=True,
                view_load=True,
                domain="[('type','=','other')]",
                readonly=True
        ),
        'int_acc': fields.property(
                'account.account',
                type='many2one',
                relation='account.account',
                string="Interest Account",
                method=True,
                view_load=True,
                domain="[('type', '=', 'other')]",
                readonly=True
        ),
        'bank_acc': fields.property(
                'account.account',
                type='many2one',
                relation='account.account',
                string="Bank Account",
                method=True,
                view_load=True,
                domain="[('type', '=', 'other')]",
                readonly=True
        ),
        'proc_fee': fields.property(
                'account.account',
                type='many2one',
                relation='account.account',
                string="Processing Fee Account",
                method=True,
                view_load=True,
                domain="[('type', '=', 'other')]",
                readonly=True
        ),                        
        'anal_acc': fields.property(
                'account.analytic.account',
                type='many2one',
                relation='account.analytic.account',
                string="Analytic Account",
                method=True,
                view_load=True,
                help="This analytic account will be used",
        ),
        'move_id' : fields.one2many('account.move.line','acc_loan_id','Move Line',readonly=True),  
        'loan_amt': fields.float('Loan Amount',digits=(12,2),required=True),
        'month': fields.integer('Loan Tenure (Months)'),
        'int_rate': fields.float('Interest Rate (Reducing)',digits=(12,2)),
        'emi_cal': fields.float('Calculated Monthly EMI',readonly=True),
        'tot_amt': fields.float('Total Amount with Interest',readonly=True),
        'flat_pa': fields.float('Flat Interest Rate PA',readonly=True),
        'flat_pm': fields.float('Flat Interest Rate PM',readonly=True),
        'tot_int_amt': fields.float('Total Interest Amount',readonly=True),
        'yr_int_amt': fields.float('Yearly Interest Amount',readonly=True),        
    }
    _defaults = {
         'auto_id': lambda obj, cr, uid, context: int(obj.pool.get('ir.sequence').get(cr, uid, 'loan.id')),
         'loan_id': lambda obj, cr, uid, context: obj.pool.get('ir.sequence').get(cr, uid, 'loan.number'),
         'state': lambda *a: 'draft',
         'apply_date': lambda *a: time.strftime('%Y-%m-%d'),
         'total_installment':lambda *a: 0.0,
         'return_type':lambda *a:'cheque',
    }
  
    def create(self,cr,uid,vals, context=None):
        cr_id = super(account_loan, self).create(cr, uid, vals, context=context)
        if vals.has_key('loan_amount') and vals['loan_amount']:
            search_ids = self.pool.get('account.loan').search(cr,uid,[('loan_id','=',vals['loan_id'])]
            read_ids = self.pool.get('account.loan').read(cr,uid,search_ids,['loan_amount'])
            for read_id in read_ids:
                del read_id['id']
                read_id['loan_amt']=read_id

        return cr_id   
         
    def onchange_partner_id(self, cr, uid, ids, part):
        if not part:
            return {'value':{'contact': False}}
        addr = self.pool.get('res.partner').address_get(cr, uid, [part], ['default','invoice'])
        return {'value':{'contact': addr['default']}}

    def onchange_loan_period(self, cr, uid, ids, part):
        sear_list = self.pool.get('loan.installment.period').search(cr,uid,[('name','=',part)])
        value_period = self.pool.get('loan.installment.period').browse(cr, uid, sear_list[0]).period
        return {'value':{'total_installment': value_period}}

    def loan_interest_get(self,cr, uid, ids,context={}):
        loan = self.pool.get('account.loan').read(cr,uid,ids)
        loantype =  loan[0]['loan_type']
        self.pool.get('account.loan').write(cr,uid,ids,{'approve_amount':loan[0]['loan_amount'] - loan[0]['process_fee']});
        self.pool.get('account.loan').write(cr,uid,ids,{'approve_date':time.strftime('%Y/%m/%d')});
        if loantype != '':
            search_loantype = self.pool.get('account.loan.loantype').search(cr,uid,[('name','=',loan[0]['loan_type'])])
            available_versions = self.pool.get('account.loan.loantype').browse(cr,uid,search_loantype[0]).interestversion_ids
            if available_versions:
                search_validversion = self.pool.get('account.loan.loantype.interestversion').search(cr,uid,[('loantype_id','=',search_loantype[0]),('start_date','<=',loan[0]['apply_date']),('end_date','>=',loan[0]['apply_date'])])
                if search_validversion:
                    available_versionlines = self.pool.get('account.loan.loantype.interestversion').browse(cr,uid,search_validversion[0]).interestversionline_ids
                    if available_versionlines:
                        search_validversionlines = self.pool.get('account.loan.loantype.interestversionline').search(cr,uid,[('interestversion_id','=',search_validversion[0]),('min_month','<=',loan[0]['total_installment']),('max_month','>=',loan[0]['total_installment']),('min_amount','<=',loan[0]['loan_amount']),('max_amount','>=',loan[0]['loan_amount'])])
                        if search_validversionlines:
                            valid_versionline = self.pool.get('account.loan.loantype.interestversionline').browse(cr,uid,search_validversionlines[0]).rate
                            if valid_versionline:
                                self.pool.get('account.loan').write(cr, uid,ids, {'interest_rate':valid_versionline})
                            else:
                                raise osv.except_osv('Information Required','Interest Rate is Not Defined')
                        else:

                            raise osv.except_osv('Information Required','There is not valid interest versionlines availble. so please check it')
                    else:
                        raise osv.except_osv('Information Required','There is no versions Defined.')
                else:
                    raise osv.except_osv('Information Required','Interest version is Not Defined')
            else:
                raise osv.except_osv('Information Required','Interest version is Not Defined')
        else:
            raise osv.except_osv('Information Required','Loan Type is Not Defined')

    def _simple_interest_get(self, cr, uid, ids, inter_rate):
        loan = self.pool.get('account.loan').read(cr,uid,ids)
        installment_cr = self.pool.get('account.loan.installment')
        cheque_cr = self.pool.get('account.loan.bank.cheque')
        if loan[0]['partner_id']:
            part_id = loan[0]['partner_id'][0]
        else:
            raise osv.except_osv('Field Required','Please select Customer');
            
        acc_ids = False
        if loan[0]['return_type'] == 'cheque':
            obj=self.browse(cr,uid,ids)
            for b in obj:
                bank_acc = b.bank_acc.id
            bank_ids=self.pool.get('res.partner.bank').search(cr,uid,[('partner_id','=',part_id)])
            if bank_ids:
                 acc_ids=self.pool.get('account.account').search(cr,uid,[('id','=',bank_acc)])
            else:
                raise osv.except_osv('Field Required','Please select Bank Account For '+loan[0]['partner_id'][1])

        inter_sed=self.pool.get('account.loan.loantype').search(cr,uid,[('name','=',loan[0]['loan_type'])])
        if inter_sed:
            inter_cal_type = self.pool.get('account.loan.loantype').browse(cr, uid, inter_sed[0]).calculation
            if inter_cal_type:
                if inter_cal_type == 'flat':        
                    int_rate = inter_rate * 1.813
                elif inter_cal_type == 'reducing':       
                    int_rate =  inter_rate
                    
        rate_interest = int_rate / 100
        total = loan[0]['loan_amount']
        installment = round(((total*(rate_interest/12))/(1-((1+rate_interest/12)**-(loan[0]['total_installment'])))))
        i = 1
        j = 1
        interest = 0
        date_update = datetime.date(2000,01,07)
        date_new = date.today()
        if date_update != date_new:
            new_month = date_new.month
            new_year = date_new.year
            date_update = date_update.replace(month=new_month)
            date_update = date_update.replace(year=new_year)
        present_month = date_update.month
        chq  = [1,2]
        cnt = 0
        while i <= loan[0]['total_installment']:
            interest_month = round(((total*rate_interest)/12))
            principle_amount = round(installment - interest_month)
            remain_amount = round(total - principle_amount)
            if loan[0]['return_type'] == 'cheque':
                present_month +=1
                if present_month>12:
                    present_month = 1;
                    s = date_update.year + 1
                    date_update=date_update.replace(year=s);
                
                date_update=date_update.replace(month=present_month);
                j += 1;              
                cheque_cr.create(cr, uid, {'name':'cheque'+str(i),'date':date_update,'loan_id':ids[0],'code':'cheque'+str(i),'partner_id':part_id,'loan_bank_id':bank_ids[0],'account_id': acc_ids[0],'cheque_amount':installment,'loan':principle_amount,'interest':interest_month})

            search_ids = cheque_cr.search(cr,uid,[('loan_id','=',ids)])

            read_ids = cheque_cr.read(cr,uid,search_ids,[])
            for read_id in read_ids:
                chq = read_id['id']            
            installment_cr.create(cr,uid,{'name':'installment'+str(i),'loan_id':ids[0],'capital':principle_amount,'interest':interest_month,'total':installment,'cheque_id':chq})            
            total = remain_amount
            interest += interest_month
            i+= 1
        self.pool.get('account.loan').write(cr,uid,ids,{'interest':interest});

        d_l = self.read(cr,uid,ids,['apply_date'])[0]
        pool = pooler.get_pool(cr.dbname)
        curr_date = d_l['apply_date']

        sal_obj = self.browse(cr, uid, ids[0])   

        gross = sal_obj.loan_amount
        pr_fee = sal_obj.process_fee
        amt = sal_obj.approve_amount

        emp_name = sal_obj.partner_id.name

        emp_obj = sal_obj.partner_id    

        period_id = pool.get('account.period').search(cr,uid,[('date_start','<=',curr_date),('date_stop','>=',curr_date)])[0]
        journal_id = pool.get('account.journal').search(cr,uid,[('name','=','x Bank Journal')])[0]
        move = {'name': '/', 'journal_id': journal_id,'period_id' :period_id, 'date': curr_date}
        move_id = self.pool.get('account.move').create(cr, uid, move)  
        acc_move_line_name = emp_name

        try:
            pool.get('account.move.line').create(cr,uid,{'move_id':move_id,'acc_loan_id': ids[0],'name': acc_move_line_name,'date': curr_date, 'account_id':sal_obj.proc_fee.id, 'credit': pr_fee ,'debit':0.0, 'journal_id' : 5,'period_id' :period_id})            
            pool.get('account.move.line').create(cr,uid,{'move_id':move_id,'acc_loan_id': ids[0],'name': acc_move_line_name,'date': curr_date, 'account_id':sal_obj.partner_id.property_account_payable.id, 'credit': amt ,'debit':0.0, 'journal_id' : 5,'period_id' :period_id})
        except:
            raise osv.except_osv('Error', 'Could not create account move lines. ')
        
        try:
            pool.get('account.move.line').create(cr,uid,{'move_id':move_id,'acc_loan_id': ids[0],'name': acc_move_line_name,'date': curr_date, 'account_id': sal_obj.cus_pay_acc.id,'debit': gross ,'credit' : 0.0,'journal_id' : 5,'period_id' :period_id})
        except:
            raise osv.except_osv('Error', 'Could not create account move line. ')

    def reject_loan(self, cr, uid, ids,context = {}):
        for loan in self.browse(cr, uid, ids):
            if loan.voucher_id and loan.voucher_id.state not in ('draft','cancel'):
                raise osv.except_osv(
                   'Could not Reject Loan !',
                   'You must first cancel invoice attaced to this loan.')


        installment_cr = self.pool.get('account.loan.installment')
        install_ids = installment_cr.search(cr,uid,[('loan_id','=',ids[0])]);
        installment_cr.unlink(cr,uid,install_ids);

        cheque_cr = self.pool.get('account.loan.bank.cheque')
        chq_ids = cheque_cr.search(cr,uid,[('loan_id','=',ids[0])]);
        cheque_cr.unlink(cr,uid,chq_ids);
        
        acc_move_line = self.pool.get('account.move.line')
        ac_ids =  acc_move_line.search(cr,uid,[('acc_loan_id','=',ids[0])]);
        acc_move_line.unlink(cr,uid,ac_ids);
        
        return True

    def proof_approval(self, cr, uid, ids,context = {}):
        loan = self.pool.get('account.loan').read(cr,uid,ids)
        loantype =  loan[0]['loan_type']
        if loantype != '':
            search_loantype = self.pool.get('account.loan.loantype').search(cr,uid,[('name','=',loantype)])
            prooftype_req = self.pool.get('account.loan.loantype').browse(cr,uid,search_loantype[0]).prooftypes
            for pt in prooftype_req:
                avail_proof_docs = self.pool.get('account.loan.proof').search(cr,uid,[('loan_id','=',ids[0]),('type','=',pt.name),('state','=','done')])
                if not avail_proof_docs:
                     raise osv.except_osv('Field Required','This loan object has not valid ' + pt.name + ' proofs so please submit proof again and valid it')
            self.pool.get('account.loan').write(cr,uid,ids,{'state':'apply'})
        else:
            raise osv.except_osv('Information Required','Loan Type is Not Defined')


    def apply_loan(self, cr, uid, ids, context = {}):
            loan = self.pool.get('account.loan').read(cr,uid,ids)
            inter_rate = loan[0]['interest_rate']
            inter_sed=self.pool.get('account.loan.loantype').search(cr,uid,[('name','=',loan[0]['loan_type'])])
            if inter_sed:
                inter_cal_type = self.pool.get('account.loan.loantype').browse(cr, uid, inter_sed[0]).calculation
                if inter_cal_type:
                    if inter_cal_type == 'flat':
                        interest_rate1= self.pool.get('account.loan')._simple_interest_get(cr, uid,ids,inter_rate)
                    elif inter_cal_type == 'reducing':
                        interest_rate1= self.pool.get('account.loan')._simple_interest_get(cr, uid,ids,inter_rate)
                else:
                    raise osv.except_osv('Field Required','Interest Type Not Selected')
            else:
                raise osv.except_osv('Field Required','Interest Type Not Defined')

    def loan_clear(self, cr, uid, ids, context={}):
        res = False
        invoices = {}
        invoice_ids = []

        def make_voucher(loan):
            b = loan.partner_id.property_account_payable.id
            
            create_ids=[]
            
            inv_id = self.pool.get('account.voucher.line').create(cr, uid, {
                    'partner_id':loan.partner_id.id,
                    'name': loan.name,
                    'amount':loan.approve_amount,
                    'account_id':b,
                    'type':'dr'
                    
            })

            create_ids.append(inv_id)
            inv = {
                'name': loan.loan_id,
                'type':'bank_pay_voucher',
                'account_id': loan.bank_acc.id,
                'narration': loan.name,
                'payment_ids': [(6,0,create_ids)],
            }
            inv_obj = self.pool.get('account.voucher')
            inv_id = inv_obj.create(cr, uid, inv)

            for o in self.pool.get('account.loan').browse(cr,uid,ids):
                self.write(cr, uid, [o.id], {'voucher_id': inv_id})
            return inv_id

        for o in self.pool.get('account.loan').browse(cr,uid,ids):
            res = make_voucher(o)
            
        return res

    def loan_paid(self, cr, uid, ids,context = {}):
        voucher_dict = {
            'draft':['open_voucher','proforma_voucher'],
            'proforma':['proforma_voucher']
        }

        voucher_pool = self.pool.get('account.voucher')

        for this_obj in self.browse(cr, uid, ids):
            voucher_obj = this_obj.voucher_id and this_obj.voucher_id or False
            voucher_state = voucher_obj and voucher_obj.state or False
            if voucher_state and voucher_state in voucher_dict:
                for voucher_method in voucher_dict[voucher_state]:
                    getattr(voucher_pool, voucher_method)(cr, uid, [this_obj.voucher_id.id],context=context)

            move_ids = voucher_obj and [x.id for x in voucher_obj.move_ids] or []

            if move_ids:
                self.pool.get('account.move.line').write(cr, uid, move_ids, {'acc_loan_id':this_obj.id})
            
        return True

    def unlink(self, cr, uid, ids, context=None):
        vouchers = self.pool.get('account.voucher').read(cr, uid, ids, ['state'])
        unlink_ids = []
        for t in vouchers:
            if t['state'] in ('draft', 'cancel'):
                unlink_ids.append(t['id'])
            else:
                raise osv.except_osv(_('Invalid action !'), _('Cannot delete vouchers(s) which are already opened or paid !'))
        osv.osv.unlink(self, cr, uid, unlink_ids, context=context)
        return True
account_loan();

class account_move_line(osv.osv):
    _inherit="account.move.line"
    _name = "account.move.line"

    _columns = {
        'acc_loan_id': fields.many2one('account.loan','Customer')
    }
account_move_line()
