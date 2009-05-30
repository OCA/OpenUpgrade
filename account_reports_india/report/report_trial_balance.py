##############################################################################
#
# Copyright (c) 2005-2006 TINY SPRL. (http://tiny.be) All Rights Reserved.
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsability of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# garantees and support are strongly adviced to contract a Free Software
# Service Company
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
##############################################################################

import time
from report import report_sxw
import rml_parse
from tools import amount_to_text_en
import pooler
import wizard

class report_trial_balance(rml_parse.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(report_trial_balance, self).__init__(cr, uid, name, context)
        self.sum_debit = 0.0
        self.sum_credit = 0.0
        self.sum_cl_bal_dr=0.0
        self.sum_cl_bal_cr=0.0
        self.total_op_dr=0.0
        self.total_op_cr=0.0
        self._sum_tra_debit = 0.0
        self._sum_tra_credit = 0.0
        self._sum_clo_debit = 0.0
        self._sum_clo_credit = 0.0
        self.localcontext.update({
            'time': time,
            'convert':self.convert,
            'sum_debit': self._sum_debit,
            'sum_credit': self._sum_credit,
            'sum_tra_debit': self.sum_tra_debit,
            'sum_tra_credit': self.sum_tra_credit,
            'sum_clo_debit': self.sum_clo_debit,
            'sum_clo_credit': self.sum_clo_credit,
            'sum_op_bal':self.sum_op_bal,
            'op_diff':self.op_diff,
            'sum_tr_bal':self.sum_tr_bal,
            'get_lines' : self.get_lines,
            'sum_cl_bal':self.sum_cl_bal,
            'get_company':self.get_company,

        })
        self.context = context
     
    def get_company(self,form):
        comp_obj=pooler.get_pool(self.cr.dbname).get('res.company').browse(self.cr,self.uid,form['company_id'])
        return comp_obj.name 
    
    def sum_cl_bal(self,move,move_other,form,year_start_date,year_end_date):
        self.sum_cl_bal_dr=0.0
        self.sum_cl_bal_cr=0.0
        res={}
        if ((self.sum_op_bal(move,move_other,form,year_start_date,year_end_date)['debit']+self.sum_tr_bal(move_other,form,year_start_date,year_end_date)['debit']) - (self.sum_op_bal(move,move_other,form,year_start_date,year_end_date)['credit']+self.sum_tr_bal(move_other,form,year_start_date,year_end_date)['credit'])) > 0:            
            self.sum_cl_bal_dr=(self.sum_op_bal(move,move_other,form,year_start_date,year_end_date)['debit']+self.sum_tr_bal(move_other,form,year_start_date,year_end_date)['debit']) - (self.sum_op_bal(move,move_other,form,year_start_date,year_end_date)['credit']+self.sum_tr_bal(move_other,form,year_start_date,year_end_date)['credit'])
        else:  
            self.sum_cl_bal_cr=((self.sum_op_bal(move,move_other,form,year_start_date,year_end_date)['debit']+self.sum_tr_bal(move_other,form,year_start_date,year_end_date)['debit']) - (self.sum_op_bal(move,move_other,form,year_start_date,year_end_date)['credit']+self.sum_tr_bal(move_other,form,year_start_date,year_end_date)['credit']))
            if self.sum_cl_bal_cr < 0.0:
                self.sum_cl_bal_cr *= -1
        res['debit']=self.sum_cl_bal_dr
        res['credit']=self.sum_cl_bal_cr
        return res
    
    def sum_op_bal(self,move,move_other,form,year_start_date,year_end_date):
        res={} 
        op_debit=0.0
        op_credit=0.0
        if move:       
            for m in move:            
                if form['date_from'] >= year_start_date and form['date_to'] <= year_end_date:
                    if m['date'] <= form['date_from']:
                       if m['date'] >= year_start_date or m['date'] < form['date_from']:
                            op_debit +=m['debit']
                            op_credit +=m['credit']              
                    if m['date'] >= form['date_from'] and m['date'] <= form['date_to']:
                        op_debit+=m['debit']
                        op_credit+=m['credit']
        if move_other:
            for m1 in move_other:
                if form['date_from'] >= year_start_date and form['date_to'] <= year_end_date:
                    if m1['date'] < form['date_from']:                        
                        if m1['date'] >= year_start_date and m1['date'] < form['date_from']:
                            op_debit +=m1['debit']
                            op_credit +=m1['credit']   
        if op_debit > op_credit:
            op_debit-=op_credit
            op_credit=0.0
        elif op_credit > op_debit:
            op_credit-=op_debit
            op_debit=0.0
        res['debit']=op_debit
        res['credit']=op_credit
        self.total_op_dr += res['debit']
        self.total_op_cr += res['credit']
        return res 
    
    def sum_tr_bal(self,move_other,form,year_start_date,year_end_date):
        res={}
        op_debit1=0.0
        op_credit1=0.0
        if move_other: 
            for m in move_other:
                if form['date_from'] >= year_start_date and form['date_to'] <= year_end_date:                    
                    if m['date'] >= form['date_from'] and m['date'] <= form['date_to']:
                        op_debit1+=m['debit']
                        op_credit1+=m['credit']
        res['debit']=op_debit1
        res['credit']=op_credit1
        return res
    
    def get_lines(self, form, ids={}):
        comp_ids=[]
        child_ids=pooler.get_pool(self.cr.dbname).get('res.company')._get_company_children(self.cr, self.uid,form['company_id'])
        if child_ids:
            comp_ids = child_ids
        else:
            comp_ids.append(form['company_id'])
        type_list=['asset','liability','income','expense']
        type_ids=pooler.get_pool(self.cr.dbname).get('account.account.type').search(self.cr, self.uid, [('code','in',type_list)])
        base_list=['Opening Stock','Purchase','Direct Expenses','Indirect Expenses','Sales Account','Goods Given Account','Direct Incomes','Indirect Incomes','Share Holder/Owner Fund','Loan(Liability) Account','Current Liabilities','Suspense Account','Fixed Assets','Investment','Current Assets','Misc. Expenses(Asset)']
        acc= pooler.get_pool(self.cr.dbname).get('account.account').search(self.cr, self.uid, [('user_type','in',type_ids),('company_id','in',comp_ids)])
        ids =acc
        if not ids:
            ids = self.ids
        if not ids:
            return []
        result = []
        context  = self.context.copy()
        context['date_from'] = form['date_from']
        context['date_to'] = form['date_to']
        context['fiscalyear'] = context={'fiscalyear': self.datas['form']['fiscalyear']}
        fiscalyear_obj =  pooler.get_pool(self.cr.dbname).get('account.fiscalyear')
        year_start_date = fiscalyear_obj.browse(self.cr, self.uid, context['fiscalyear'] ).date_start
        year_end_date = fiscalyear_obj.browse(self.cr, self.uid, context['fiscalyear'] ).date_stop 
        start_date = form['date_from']
        end_date =  form['date_to']
        accounts = self.pool.get('account.account').read(self.cr, self.uid, ids, [ 'id','code','name','level','type1','child_id' ])
        for account in accounts:
            journal_id = self.pool.get('account.journal').search(self.cr, self.uid,[('type','=','situation')])
            jnl_other_id = self.pool.get('account.journal').search(self.cr, self.uid,[('type','!=','situation')])
            move_id = self.pool.get('account.move.line').search(self.cr, self.uid, [('account_id','=', account['id']),('journal_id','in',journal_id)])
            move_other_id = self.pool.get('account.move.line').search(self.cr, self.uid, [('account_id','=', account['id']),('journal_id','in',jnl_other_id)])
            move = self.pool.get('account.move.line').read(self.cr, self.uid, move_id, ['date','debit','credit'])
            move_other = self.pool.get('account.move.line').read(self.cr, self.uid, move_other_id , ['date','debit','credit'])
            open = 0.0
            res = {
                'code': account['code'],
                'name': account['name'],
                'level': account['level'],
                'o_debit':  self.sum_op_bal(move,move_other,form,year_start_date,year_end_date)['debit'],
                'o_credit': self.sum_op_bal(move,move_other,form,year_start_date,year_end_date)['credit'],
                't_debit':  self.sum_tr_bal(move_other,form,year_start_date,year_end_date)['debit'],
                't_credit': self.sum_tr_bal(move_other,form,year_start_date,year_end_date)['credit'],
                'c_debit':  self.sum_cl_bal(move,move_other,form,year_start_date,year_end_date)['debit'],
                'c_credit': self.sum_cl_bal(move,move_other,form,year_start_date,year_end_date)['credit'],
                'type' : account['type1']
            }
            if account['child_id']:
                res['child']='1'
            else:
                res['child']='0'
            self.sum_debit += res['o_debit']
            self.sum_credit += res['o_credit']
            self._sum_tra_debit += res['t_debit']
            self._sum_tra_credit += res['t_credit']
            self._sum_clo_debit += res['c_debit']
            self._sum_clo_credit += res['c_credit']
            if form['empty_account']==False and res['name'] not in base_list:
                if res['o_debit'] or res['o_credit'] or res['t_debit'] or res['t_credit'] or res['c_debit'] and res['c_credit']:
                    result.append(res)
            else:
                result.append(res)
        return result

    def convert(self,amount, cur):
        amt_en = amount_to_text_en.amount_to_text(amount,'en',cur);
        return amt_en
    
    def op_diff(self):
        res={}
        if self.total_op_dr > self.total_op_cr:
            res['type']='dr'
            res['bal']=self.total_op_dr-self.total_op_cr
        else:
            res['type']='cr'
            res['bal']=self.total_op_cr-self.total_op_dr
        return res

    def _sum_credit(self):
        return self.sum_credit
    
    def _sum_debit(self):
        return self.sum_debit
    
    def sum_tra_credit(self):
        return self._sum_tra_credit
    
    def sum_tra_debit(self):
        return self._sum_tra_credit
    
    def sum_clo_credit(self):
        return self._sum_clo_credit
    
    def sum_clo_debit(self):
        return self._sum_clo_credit
    
report_sxw.report_sxw(
    'report.trial.balance.sheet',
    'account.account',
    'addons/account_reports_india/report/report_trial_balance.rml',
    parser=report_trial_balance, header=False
)
