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
import wizard
import time
import mx.DateTime
from report import report_sxw
from generalize_account_report.report import report_generalize_horizontal

class report_generalize_vertical(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(report_generalize_vertical, self).__init__(cr, uid, name, context)
        self.res_pl={}
        self.result_sum_dr=0.0
        self.result_sum_expense_dr=0.0
        self.result_sum_cr=0.0
        self.result_sum_income_cr=0.0
        self.result_dr=0.0
        self.result_cr=0.0
        
        self.result_sum1_dr=0.0
        self.result_sum_lib_dr=0.0
        self.result_sum1_cr=0.0
        self.result_sum_ass_cr=0.0
        self.result1_dr=0.0
        self.result1_cr=0.0

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
            'sum_lib_dr' : self.sum_lib_dr,
            'sum_ass_cr' : self.sum_ass_cr,
            'sum_lib1_dr' : self.sum_lib1_dr,
            'sum_ass1_cr' : self.sum_ass1_cr,
            'sum1_dr' : self.sum1_dr,
            'sum1_cr' : self.sum1_cr,

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

    def sum1_dr(self):
        return self.result_sum1_dr or 0.0
     
    def sum1_cr(self):
        return self.result_sum1_cr or 0.0
    
    def sum_lib_dr(self):
        return self.result_sum_lib_dr or 0.0
     
    def sum_ass_cr(self):
        return self.result_sum_ass_cr or 0.0
    
    def sum_lib1_dr(self):
        return self.result1_dr or 0.0
     
    def sum_ass1_cr(self):
        return self.result1_cr or 0.0

    def get_data(self,obj,level=0):
        if obj.final_type == 'pl':
            gr_list=['expense','income']
        if obj.final_type == 'bs':
            res_pl={}
            gr_list=['liability','asset']
            pl_id_l = self.pool.get('generalize.account.report').search(self.cr,self.uid,[('final_type','=','pl')])
            if not pl_id_l:
                return wizard.except_wizard(_('Configration Error !'), _('Please First Define Profit and Loss Object and then Balance Sheet.'))
            else:
                pl_obj = self.pool.get('generalize.account.report').browse(self.cr,self.uid,pl_id_l)
                for pl in pl_obj:
                    if pl.type == 'vertical':
                        result_pl=self.get_data(pl)
                        res_pl=self.final_result()
                if res_pl == {}:
                    return wizard.except_wizard(_('Configration Error !'), _('Please First Define Profit and Loss Object With The Same Type and then Balance Sheet.'))
                resp={}
                result=[]
                if res_pl['type']== 'Net Profit':
                    res_pl['balance'] *= -1
        for group in gr_list:
            if group=='expense':
                list_acc = []
                for l in obj.gr_detail:
                    if l.pos_name == 'top':
                        list_acc.append(l.acc_gr_name.name)
            if group=='income':
                list_acc = []
                for l in obj.gr_detail:
                    if l.pos_name == 'bottom':
                        list_acc.append(l.acc_gr_name.name)
            if group=='liability':
                list_acc = []
                for l in obj.gr_detail:
                    if l.pos_name == 'top':
                        list_acc.append(l.acc_gr_name.name)
            if group=='asset':
                list_acc = []
                for l in obj.gr_detail:
                    if l.pos_name == 'bottom':
                        list_acc.append(l.acc_gr_name.name)
            acc_objs=[]
            final_result={}
            balance_dict={}
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
#            comp_ids=[]
#            c_child_ids=pooler.get_pool(self.cr.dbname).get('res.company')._get_company_children(self.cr, self.uid,form['company_id'])
#            if c_child_ids:
#                comp_ids = c_child_ids
#            else:
#                comp_ids.append(form['company_id'])
            for lacc in list_acc:
                acc_ids +=self.pool.get('account.account').search(self.cr, self.uid, [('name','=', lacc),('company_id','=',obj.company_id.id)])
            ids2 = self.pool.get('account.account')._get_children_and_consol(self.cr, self.uid, acc_ids, context)
            acc_objs=self.pool.get('account.account').browse(self.cr, self.uid, ids2)
            balance_dict=self.pool.get('account.account').compute_total(self.cr,self.uid,ids2,year_start_date,year_end_date,obj.st_date,obj.end_date,{'debit': 0.0,'credit': 0.0, 'balance': 0.0})
            for aobj in acc_objs:
                res={}
                res['name']=aobj.name
                res['balance']=balance_dict[aobj.id]['balance']
                res['type']=group
                res['parent_id'] = aobj.parent_id
                if aobj.name in list_acc:
                    res['level']=0
                else:
                    if aobj.parent_id:
                        for r in result:
                            if r['name']== aobj.parent_id.name:
                                res['level'] = r['level'] + 1
                                break
                if res['level'] > 1:
                    res['outer']='-1'
                    if res['type'] == 'expense':
                         self.result_dr +=res['balance']
                    if res['type'] == 'income':
                         self.result_cr +=res['balance']
                    if res['type'] == 'liability':
                         self.result1_dr +=res['balance']
                    if res['type'] == 'asset':
                         self.result1_cr +=res['balance']
                if res['level']== 1:
                    res['outer']='0'
                    if res['type'] == 'expense':
                         self.result_sum_expense_dr +=res['balance']
                    if res['type'] == 'income':
                         self.result_sum_income_cr +=res['balance']
                    if res['type'] == 'liability':
                         self.result_sum_lib_dr +=res['balance']
                    if res['type'] == 'asset':
                         self.result_sum_ass_cr +=res['balance']
                  
                if res['level']== 0 :
                    res['outer']='1'
                    if res['type'] == 'expense':
                        self.result_sum_dr +=res['balance']
                    if res['type'] == 'income':
                        self.result_sum_cr +=res['balance']
                    if res['type'] == 'liability':
                        self.result_sum1_dr +=res['balance']
                    if res['type'] == 'asset':
                        self.result_sum1_cr +=res['balance']
                if obj.final_type == 'bs':
                    if res_pl['type']=='Net Profit' and res['name']==obj.profit_tran_acc.name:
                        resp['outer']='-1'
                        resp['name']= res_pl['type']
                        resp['type']=res['type']
                        resp['level']=res['level'] + 1
                        resp['balance']=res_pl['balance']
                        res['parent_id'] = obj.profit_tran_acc
                        self.result_sum_lib_dr +=resp['balance']
                        self.result_sum1_dr +=resp['balance']
                        self.result1_dr +=resp['balance']
                        res['balance'] += resp['balance']
                    if res_pl['type']=='Net Loss' and res['name']==obj.Loss_tran_acc.name:
                        resp['outer']='0'
                        resp['name']= res_pl['type']
                        resp['type']=res['type']
                        resp['level']=res['level'] +1
                        resp['balance']=res_pl['balance']
                        res['parent_id'] = obj.Loss_tran_acc
                        self.result_sum_ass_cr +=resp['balance']
                        self.result_sum1_cr +=resp['balance']
                        res['balance'] += resp['balance']
                        
                result.append(res)
                if obj.final_type == 'bs': 
                    if res_pl['type']=='Net Profit' and res['name']==obj.profit_tran_acc.name:
                        for rt in result:
                            if rt['parent_id']:
                               rt['balance'] += resp['balance']
                               if res['name']==obj.profit_tran_acc.name:
                                   break
                        result.append(resp)
                    if res_pl['type']=='Net Loss' and res['name']==obj.Loss_tran_acc.name:
                        for rt in result:
                            if rt['parent_id']:
                               rt['balance'] += resp['balance']
                               if res['name']==obj.Loss_tran_acc.name:
                                   break
                        result.append(resp)
            if obj.final_type == 'pl':
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
            final_result['gr_name']=group
            final_result['list']=result
            self.final.append(final_result)
        return None
    
    def get_acc_obj(self,obj_list,group):
        result=[]
        for obj_acc in obj_list:
            if obj_acc.type == group:
                result.append(obj_acc)       
        return result

    def get_lines(self,group):
        result=[]
        for list in self.final:
            if list['gr_name']== group:
                result=list['list']
                break
        return result
    
report_sxw.report_sxw('report.generalize.vertical', 'generalize.account.report',
    'generalize_account_report/report/report_generalize_vertical.rml',parser=report_generalize_vertical,
    header=False)
