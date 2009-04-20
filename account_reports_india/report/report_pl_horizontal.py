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
import rml_parse
from report import report_sxw

class report_pl_account_horizontal(rml_parse.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(report_pl_account_horizontal, self).__init__(cr, uid, name, context)
        self.result_sum_dr=0.0
        self.result_sum_expense_dr=0.0
        self.result_sum_cr=0.0
        self.result_sum_income_cr=0.0
        self.result_dr=0.0
        self.result_cr=0.0
        self.res_pl ={}
        self.result_temp=[]
        self.localcontext.update( {
            'time': time,
            'get_lines' : self.get_lines,
            'get_company': self.get_company,
            'get_currency': self._get_currency,
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
        return self.result_sum_dr or 0.0
     
    def sum_cr(self):
        return self.result_sum_cr or 0.0

    def sum_expense_dr(self):
        return self.result_sum_expense_dr or 0.0
     
    def sum_income_cr(self):
       return self.result_sum_income_cr or 0.0

    def sum_expense1_dr(self):
        return self.result_dr or 0.0

    def sum_income1_cr(self):
        return self.result_cr or 0.0

    def get_data(self,form):
        gr_list=['expense','income']
        base_list=['Opening Stock','Purchase','Direct Expenses','Indirect Expenses','Sales Account','Goods Given Account','Direct Incomes','Indirect Incomes']
        cal_list={}
        for group in gr_list:
            if group=='expense':
                list_acc=['Opening Stock','Purchase','Direct Expenses','Indirect Expenses']
            if group=='income':
                list_acc=['Sales Account','Goods Given Account','Direct Incomes','Indirect Incomes']
            acc_objs=[]
            final_result={}
            balance_dict={}
            result=[]
            result_temp=[]
            res={}
            acc_ids=[]
            context  = self.context.copy()
            context['fiscalyear'] = context={'fiscalyear': form['fiscalyear']}
            fiscalyear_obj =  pooler.get_pool(self.cr.dbname).get('account.fiscalyear')
            date_obj=fiscalyear_obj.browse(self.cr, self.uid, context['fiscalyear'])
            year_start_date = date_obj.date_start
            year_end_date = date_obj.date_stop  
            comp_ids=[]
            c_child_ids=pooler.get_pool(self.cr.dbname).get('res.company')._get_company_children(self.cr, self.uid,form['company_id'])
            if c_child_ids:
                comp_ids = c_child_ids
            else:
                comp_ids.append(form['company_id'])
            for lacc in list_acc:
                acc_ids +=self.pool.get('account.account').search(self.cr, self.uid, [('name','=', lacc),('company_id','in',comp_ids)])
            if form['display_type'] == 'consolidated':
                ids2= acc_ids
            else:
                ids2 = self.pool.get('account.account')._get_children_and_consol(self.cr, self.uid, acc_ids, context)
            acc_objs=self.pool.get('account.account').browse(self.cr, self.uid, ids2)
            balance_dict=self.pool.get('account.account').compute_total(self.cr,self.uid,ids2,year_start_date,year_end_date,form['date1'],form['date2'],{'debit': 0.0,'credit': 0.0, 'balance': 0.0})
            for aobj in acc_objs:
                res={}
                res['name']=aobj.name
                res['balance']=balance_dict[aobj.id]['balance']
                res['type']=aobj.user_type.code
                res['level']=aobj.level
                if res['level']== False:
                    if aobj.parent_id:
                        for r in result:
                            if r['name']== aobj.parent_id.name:
                                res['level'] = r['level'] + 1
                                break
                if res['level'] > 4:
                    res['outer']='-1'
                    if res['type'] == 'expense':
                         self.result_dr +=res['balance']
                    else:
                         self.result_cr +=res['balance']
                         
                if res['level']== 4:
                    res['outer']='0'
                    if res['type'] == 'expense':
                         self.result_sum_expense_dr +=res['balance']
                    else:
                         self.result_sum_income_cr +=res['balance']
                    
                if res['level']== 3 or res['level'] < 3:
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
                cal_list[group]=result
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
        if cal_list:   
            temp={}
            for i in range(0,max(len(cal_list['expense']),len(cal_list['income']))):
                if i < len(cal_list['expense']) and i < len(cal_list['income']):
                    temp={
                          'name' : cal_list['expense'][i]['name'],
                          'type' : cal_list['expense'][i]['type'],
                          'level': cal_list['expense'][i]['level'],
                          'outer': cal_list['expense'][i]['outer'],
                          'balance':cal_list['expense'][i]['balance'],
                          'name1' : cal_list['income'][i]['name'],
                          'type1' : cal_list['income'][i]['type'],
                          'level1': cal_list['income'][i]['level'],
                          'outer1': cal_list['income'][i]['outer'],
                          'balance1':cal_list['income'][i]['balance'],
                          }
                    self.result_temp.append(temp)
                else:
                    if i < len(cal_list['income']):
                        temp={
                              'name' : '',
                              'type' : '',
                              'level': False,
                              'outer': False,
                              'balance':False,
                              'name1' : cal_list['income'][i]['name'],
                              'type1' : cal_list['income'][i]['type'],
                              'level1': cal_list['income'][i]['level'],
                              'outer1': cal_list['income'][i]['outer'],
                              'balance1':cal_list['income'][i]['balance'],
                              }
                        self.result_temp.append(temp)
                    if  i < len(cal_list['expense']): 
                        temp={
                              'name' : cal_list['expense'][i]['name'],
                              'type' : cal_list['expense'][i]['type'],
                              'level': cal_list['expense'][i]['level'],
                              'outer': cal_list['expense'][i]['outer'],
                              'balance':cal_list['expense'][i]['balance'],
                              'name1' : '',
                              'type1' : '',
                              'level1': False,
                              'outer1': False,
                              'balance1':False,
                              }
                        self.result_temp.append(temp)
        return None
    
    def get_acc_obj(self,obj_list,group):
        result=[]
        for obj_acc in obj_list:
            if obj_acc.type == group:
                result.append(obj_acc)       
        return result

    def get_lines(self):
        return self.result_temp
    
    def _get_currency(self, form):
        return pooler.get_pool(self.cr.dbname).get('res.company').browse(self.cr, self.uid, form['company_id']).currency_id.code

    def get_company(self,form):
        comp_obj=pooler.get_pool(self.cr.dbname).get('res.company').browse(self.cr,self.uid,form['company_id'])
        return comp_obj.name

report_sxw.report_sxw('report.pl.account.horizontal', 'account.account',
    'addons/account_reports_india/report/report_pl_account_horizontal.rml',parser=report_pl_account_horizontal, header=False)

