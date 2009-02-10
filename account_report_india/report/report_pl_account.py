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

import pooler
import time
import mx.DateTime
from report import report_sxw

class report_pl_account(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(report_pl_account, self).__init__(cr, uid, name, context)
        self.result_sum_dr=0.0
        self.result_sum_expense_dr=0.0
        self.result_sum_cr=0.0
        self.result_sum_income_cr=0.0
        self.result_dr=0.0
        self.result_cr=0.0
        self.res_pl ={}
        self.final=[]
        self.localcontext.update( {
            'time': time,
            'get_lines' : self.get_lines,
            'get_data': self.get_data,
            'sum_dr' : self.sum_dr,
            'sum_cr' : self.sum_cr,
            'sum_expense_dr' : self.sum_expense_dr,
            'sum_income_cr' : self.sum_income_cr,
            'sum_expense1_dr' : self.sum_expense1_dr,
            'sum_income1_cr' : self.sum_income1_cr,
            'final_result' : self.final_result,
            'get_acc_obj':self.get_acc_obj,
        })
        self.context = context
        
    def final_result(self):
        return self.res_pl
    
    def sum_dr(self):
        if self.result_sum_dr < 0.0:
            self.result_sum_dr *= -1
        return self.result_sum_dr or 0.0
     
    def sum_cr(self):
        if self.result_sum_cr < 0.0:
            self.result_sum_cr *= -1
        return self.result_sum_cr or 0.0

    def sum_expense_dr(self):
        if self.result_sum_expense_dr < 0.0:
            self.result_sum_expense_dr *= -1
        return self.result_sum_expense_dr or 0.0
     
    def sum_income_cr(self):
        if self.result_sum_income_cr < 0.0:
            self.result_sum_income_cr *= -1
        return self.result_sum_income_cr or 0.0

    def sum_expense1_dr(self):
        if self.result_dr < 0.0:
            self.result_dr *= -1
        return self.result_dr or 0.0

    def sum_income1_cr(self):
        if self.result_cr < 0.0:
            self.result_cr *= -1
        return self.result_cr or 0.0

    def get_data(self,obj,form):
        gr_list=['expense','income']
        if obj.group_type == 'pl_accounts_group':
            base_list=['Opening Stock','Purchase','Direct Expenses','Indirect Expenses','Sales Account','Goods Given Account','Direct Incomes','Indirect Incomes']
            for group in gr_list:
                acc_objs=[]
                final_result={}
                result=[]
                result_temp=[]
                res={}
                acc_ids=[]
                context  = self.context.copy()
                context['fiscalyear'] = context={'fiscalyear': obj.fiscal_year.id}
                fiscalyear_obj =  pooler.get_pool(self.cr.dbname).get('account.fiscalyear')
                date_obj=fiscalyear_obj.browse(self.cr, self.uid, context['fiscalyear'])
                year_start_date = date_obj.date_start
                year_end_date = date_obj.date_stop 
                acc_objs=self.get_acc_obj(obj.acc_detail,group) 
                for aobj in acc_objs:
                    res={}
                    res['name']=aobj.name
                    res['balance']=aobj.balance
                    res['type']=aobj.type
                    res['level']=aobj.level
                    if res['level'] > 1:
                        res['outer']='-1'
                        if res['type'] == 'expense':
                             self.result_dr +=res['balance']
                        else:
                             self.result_cr +=res['balance']
                             
                    if res['level']== 1:
                        res['outer']='0'
                        if res['type'] == 'expense':
                             self.result_sum_expense_dr +=res['balance']
                        else:
                             self.result_sum_income_cr +=res['balance']
                        
                    if res['level']== 0:
                        res['outer']='1'
                        if res['type'] == 'expense':
                            self.result_sum_dr +=res['balance']
                        else:
                            self.result_sum_cr +=res['balance']
                    if form['empty_account']==False and res['name'] not in base_list:
                        if res['balance']:
                         if form['display_type'] == 'consolidated':
                            if res['name'] in base_list:
                                result.append(res)  
                         else:
                            result.append(res) 
                    else:
                        if form['display_type'] == 'consolidated':
                            if res['name'] in base_list:
                                result.append(res)  
                        else:
                            result.append(res) 
                final_result['gr_name']=group
                final_result['list']=result
                self.final.append(final_result)
            if self.result_sum_dr < 0.0:
                self.result_sum_dr *= -1
            if self.result_sum_cr < 0.0:
                self.result_sum_cr *= -1
            if self.result_sum_dr > self.result_sum_cr:
                self.res_pl['type']='Net Loss'
                self.res_pl['balance']=(self.result_sum_dr - self.result_sum_cr)
            else:
                self.res_pl['type']='Net Profit'
                self.res_pl['balance']=(self.result_sum_cr - self.result_sum_dr)    
        return None
    
    def get_acc_obj(self,obj_list,group):
        done=[]
        result=[]
        for obj_acc in obj_list:
            if obj_acc.name not in done:
                done.append(obj_acc.name)
                if obj_acc.type == group or obj_acc.type=='asset':
                    result.append(obj_acc)       
        return result

    def get_lines(self,group):
        result=[]
        for list in self.final:
            if list['gr_name']== group:
                result=list['list']
        return result

report_sxw.report_sxw('report.pl.account', 'account.report.india',
    'addons/account_report_india/report/report_pl_account.rml',parser=report_pl_account,
    header=False)

