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

import ir
import time
import pooler
from osv import osv
from osv import fields

class account_loan_bank_cheque(osv.osv):
    _name='account.loan.bank.cheque'
    _description='Bank Account Cheque'
    _rec_name = 'code'
    _columns={
        'loan_id':fields.many2one('account.loan','Loan', required=False),
        'code':fields.char('Code', size=32, required=True),
        'name':fields.char('Name', size=32,required=True),
        'partner_id':fields.many2one('res.partner', 'Customer', required=True),
        'loan_bank_id':fields.many2one('res.partner.bank','Bank', required=True),
        'loan':fields.float('Loan Amount', size=32),
        'interest':fields.float('Interest Amount', size=32),
        'cheque_amount':fields.float('Cheque Amount', size=32, required=True),
        'account_id':fields.many2one('account.account', 'General Account', required=True, select=True),
        'state':fields.selection([
                ('draft','Draft'),
                ('posted','Posted'),
                ('clear','Clear'),
                ('return','Return'),
                ('cancel','Cancel'),
                ('done','Done')
            ],'State', readonly=True, select=True),
        'date':fields.date('Date', required=True),
        'clear_date':fields.date('Cheque Clearing Date', required=False, readonly=True),
        'return_date':fields.date('Cheque Return Date', required=False, readonly=True),
        'note':fields.text('Notes'),
        'cheque_id' :fields.one2many('account.loan.installment','cheque_id','Installments'),
        'voucher_id': fields.many2one('account.voucher', 'Voucher',readonly=True),
    }
    _defaults={
       'state':lambda *a:'draft',
       'date': lambda *a: time.strftime('%Y-%m-%d'),
    }

    def onchange_bank_id(self, cr, uid, ids, part):
        val={'loan_bank_id': False,'account_id':False,'loan_id':False}
        if not part:
            return {'value':val}
        else:
            bank_ids=self.pool.get('res.partner.bank').search(cr,uid,[('partner_id','=',part)])
            loan_ids=self.pool.get('account.loan').search(cr,uid,[('partner_id','=',part)])
            obj=self.pool.get('account.loan').browse(cr,uid,part)
            bank_acc = obj.bank_acc.id
            if loan_ids.__len__()>0:
                val['loan_id']=loan_ids[0];
            if bank_ids.__len__()>0:
                acc_ids=self.pool.get('account.account').search(cr,uid,[('id','=',bank_acc)])
               
                if acc_ids:
                    val['loan_bank_id']=bank_ids[0];
                    val['account_id']=acc_ids[0];
                    return {'value':val}
                else:
                    val['loan_bank_id']=bank_ids[0];
                    return {'value':val}
            else:
                return {'value':val}

    def post_bank(self, cr, uid, ids, context={}):
        res = False
        invoices = {}
        invoice_ids = []

        def make_voucher(loan):
            b = loan.partner_id.property_account_payable.id
            ln_id = loan.loan_id
            int_acc = ln_id.int_acc.id
            cus_acc = ln_id.cus_pay_acc.id
            create_ids=[]
            
            inv_id = self.pool.get('account.voucher.line').create(cr, uid, {
                'partner_id':loan.partner_id.id,
                'name': loan.name,
                'amount':loan.loan,
                'account_id':cus_acc,
                'type':'cr'
            })
                    
            inv_id1 = self.pool.get('account.voucher.line').create(cr, uid, {
                'partner_id':loan.partner_id.id,
                'name': loan.name,
                'amount':loan.interest,
                'account_id':int_acc,
                'type':'cr'
            })
            create_ids.append(inv_id1)
            create_ids.append(inv_id)
            
            inv = {
                'name': loan.loan_id.loan_id,
                'type':'bank_rec_voucher',
                'account_id': loan.account_id.id,
                'narration': loan.name,
                'payment_ids': [(6,0,create_ids)],
                'date':loan.date
            }

            inv_obj = self.pool.get('account.voucher')
            inv_id = inv_obj.create(cr, uid, inv)
            for o in self.pool.get('account.loan').browse(cr,uid,ids):
                self.write(cr, uid, [o.id], {'voucher_id': inv_id})           
            return inv_id

        for o in self.pool.get('account.loan.bank.cheque').browse(cr,uid,ids):
            res = make_voucher(o)
            
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
                self.pool.get('account.move.line').write(cr, uid, move_ids, {'acc_loan_id':this_obj.loan_id.id})
         
        return res
        
    def cheque_return(self, cr, uid, ids, context={}):
        for o in self.pool.get('account.loan.bank.cheque').browse(cr,uid,ids):
            self.write(cr, uid, [o.id], {'return_date': time.strftime('%Y-%m-%d')})

        res = False
        invoices = {}
        invoice_ids = []

        def make_voucher(loan):
            b = loan.partner_id.property_account_payable.id
            ln_id = loan.loan_id
            int_acc = ln_id.int_acc.id
            cus_acc = ln_id.cus_pay_acc.id
            create_ids=[]
            
            inv_id = self.pool.get('account.voucher.line').create(cr, uid, {
                'partner_id':loan.partner_id.id,
                'name': loan.name,
                'amount':loan.loan,
                'account_id':cus_acc,
                'type':'dr'
            })
            inv_id1 = self.pool.get('account.voucher.line').create(cr, uid, {
                'partner_id':loan.partner_id.id,
                'name': loan.name,
                'amount':loan.interest,
                'account_id':int_acc,
                'type':'dr'
            })
            create_ids.append(inv_id1)
            create_ids.append(inv_id)
            
            inv = {
                'name': loan.loan_id.loan_id,
                'type':'bank_pay_voucher',
                'account_id': loan.account_id.id,
                'narration': loan.name,
                'payment_ids': [(6,0,create_ids)],
                'date':loan.date
            }
            inv_obj = self.pool.get('account.voucher')
            inv_id = inv_obj.create(cr, uid, inv)
            for o in self.pool.get('account.loan').browse(cr,uid,ids):
                self.write(cr, uid, [o.id], {'voucher_id': inv_id})           
            return inv_id

        for o in self.pool.get('account.loan.bank.cheque').browse(cr,uid,ids):
            res = make_voucher(o)
            
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
                self.pool.get('account.move.line').write(cr, uid, move_ids, {'acc_loan_id':this_obj.loan_id.id})  
        return res

    def cheque_clear(self, cr, uid, ids, context={}):
        res = False  
        for o in self.pool.get('account.loan.bank.cheque').browse(cr,uid,ids):
            self.write(cr, uid, [o.id], {'clear_date': time.strftime('%Y-%m-%d')})
            
        print res    

account_loan_bank_cheque()
