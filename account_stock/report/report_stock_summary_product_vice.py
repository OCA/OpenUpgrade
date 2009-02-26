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
from report import report_sxw

class report_stock_summary_product_vice(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(report_stock_summary_product_vice, self).__init__(cr, uid, name, context)
        self.done=[]
        self.test1=[]
        self.list_sale=[]
        self.line_data=[]
        self.wavg_qty=0
        self.wavg_rate=0.0
        self.wavg_amt=0.0
        self.count=0
        self.count_list=[]
        self.wavg_list_outward=[]
        self.p_qty=0
        self.p_rate=0.0
        self.p_amt=0.0
        self.localcontext.update( {
            'time': time,
            'get_product_line': self.get_product_line,
            'get_line_detail': self.get_line_detail,
            'get_line':self.get_line,
            'get_balance':self.get_balance,
            'get_list':self.get_list,
            'sortDictBy':self.sortDictBy,
            'get_list_sale':self.get_list_sale,
            'get_method_mode':self.get_method_mode,
            'get_company':self.get_company,
            })

    def get_company(self,form):
        res={}
        comp_obj=pooler.get_pool(self.cr.dbname).get('res.company').browse(self.cr,self.uid,form['company_id'])
        res['comp_obj']=comp_obj
        res['comp_name']=comp_obj.name
        return res 

    def get_method_mode(self,form):
        res={}
        res['method']=form['method'].swapcase()
        res['mode']=form['mode'].swapcase()
        return res
    
    def get_list(self):
        for t in self.test1:
            if t['qty']< 0 and t['amt']<0:
                t['qty']*=-1
                t['amt']*=-1
        return self.test1
    
    def get_list_sale(self):
        return self.list_sale

    def get_balance(self,final,pname,form):
        sale_dict={}
        test_dict={}
        result=[]
        res={}
        res_qty=0
        res_rate=0.0
        res_amt=0.0
        temp={
              'temp_qty':0,
              'temp_rate':0.0,
              'temp_amt':0.0
              }
        temp1={
              'temp_qty':0,
              'temp_rate':0.0,
              'temp_amt':0.0
              }
        temp2={
              'temp_qty':0,
              'temp_rate':0.0,
              'temp_amt':0.0
              }
        if pname not in self.done:
            self.test1=[]
            self.list_sale=[]
            self.p_qty = 0
            self.p_rate= 0.0
            self.p_amt = 0.0
            self.done.append(pname)
        if form['method']=='weighted avg':
            if final['type']=='inward':
                self.p_qty += final['qty']
                self.p_amt  +=final['amt']
                res['bal_qty']=self.p_qty
                res['bal_rate']=(self.p_amt/self.p_qty)
                res['bal_amt']=self.p_amt
                res['gp']=''  
                self.wavg_qty=self.p_qty
                self.wavg_rate=(self.p_amt/self.p_qty)
                self.wavg_amt=self.p_amt  
            else:
                self.p_qty -= final['qty']
                self.p_amt=(self.wavg_rate*int(final['qty']))
                if self.p_qty >0:
                    res['bal_qty']=self.p_qty
                    res['bal_rate']= self.wavg_rate
                    res['bal_amt']=(self.wavg_amt-self.p_amt)
                    temp1['temp_amt']='%.2f' %(((final['amt']-self.p_amt)*100)/self.p_amt)
                    res['gp']=str(temp1['temp_amt']) + "%"
                    self.wavg_qty=self.p_qty
                    self.wavg_rate=self.wavg_rate
                    self.wavg_amt=(self.wavg_amt-self.p_amt)
                    sale_dict={
                                 'date':final['date'],
                                 'inv_no':final['inv_no'],
                                 'type':final['type'],
                                 'rate':self.wavg_rate,
                                 'amt':self.p_amt,
                                 'qty':final['qty'],
                                 'uos':final['uos'],
                               }
                    self.list_sale.append(sale_dict)
                else:
                    res['bal_qty']="0"
                    res['bal_rate']= 0.0
                    res['bal_amt']=0.0
                    res['gp']='0.0%'

            self.test1=[{
                         'date':final['date'],
                         'inv_no':final['inv_no'],
                         'type':final['type'],
                         'rate':res['bal_rate'],
                         'amt':res['bal_amt'],
                         'qty':res['bal_qty'],
                         'uos':final['uos'],         
                         }]
        if form['method']=='simple avg':
            if final['type']=='inward':
                self.count += 1
                self.count_list.append(final)
                self.p_qty += final['qty']
                self.p_rate+=final['rate']
                self.p_amt  +=final['amt']
                res['bal_qty']=self.p_qty
                res['bal_rate']=self.p_rate/len(self.count_list)
                res['bal_amt']=self.p_amt  
                res['gp']=''
                self.wavg_qty=self.p_qty
                self.wavg_rate=self.p_rate/len(self.count_list)
                self.wavg_amt=self.p_amt  
            else:
                self.count_list=[]
                self.p_qty -= final['qty']
                self.p_amt=(self.wavg_rate*int(final['qty']))
                if self.p_qty > 0:
                    res['bal_qty']=self.p_qty
                    res['bal_rate']= self.wavg_rate
                    res['bal_amt']=(self.wavg_amt-self.p_amt)
                    temp1['temp_amt']='%.2f' %(((final['amt']-self.p_amt)*100)/self.p_amt)
                    res['gp']=str(temp1['temp_amt']) + "%"
                    self.count_list.append(res)
                    self.p_rate=res['bal_rate']
                    self.count = 1
                    self.wavg_qty=self.p_qty
                    self.wavg_rate=self.wavg_rate
                    self.wavg_amt=(self.wavg_amt-self.p_amt)
                    sale_dict={
                                 'date':final['date'],
                                 'inv_no':final['inv_no'],
                                 'type':final['type'],
                                 'rate':self.wavg_rate,
                                 'amt':self.p_amt,
                                 'qty':final['qty'],
                                 'uos':final['uos'],
                               }
                    self.list_sale.append(sale_dict)
                else:
                    res['bal_qty']="0"
                    res['bal_rate']= 0.0
                    res['bal_amt']=0.0
                    res['gp']='0.0%'
            self.test1=[{
                         'date':final['date'],
                         'inv_no':final['inv_no'],
                         'type':final['type'],
                         'rate':res['bal_rate'],
                         'amt':res['bal_amt'],
                         'qty':res['bal_qty'],
                         'uos':final['uos'],         
                         }]             
        if form['method']=='fifo' or form['method']=='lifo':
            if final['type']=='inward':
                self.test1.append(final)
                self.p_qty += final['qty']
                self.p_amt  +=final['amt']
                res['bal_qty']=self.p_qty
                res['bal_rate']=(self.p_amt/self.p_qty)
                res['bal_amt']=(self.p_amt)
                res['gp']=''
            else:   
                t_amt1=0.0
                t_amt2=0.0
                diff=0.0
                if form['method']=='fifo':
                    if self.test1!=[]:
                        temp['temp_qty']=self.test1[0]['qty']
                        temp['temp_rate']=self.test1[0]['rate']  
                        temp['temp_amt']=self.test1[0]['amt']
                if form['method']=='lifo':
                    if self.test1!=[]:
                        temp['temp_qty']=self.test1[-1]['qty']
                        temp['temp_rate']=self.test1[-1]['rate']  
                        temp['temp_amt']=self.test1[-1]['amt']
                if final['qty'] > temp['temp_qty']:
                    sale_dict={
                                 'date':final['date'],
                                 'inv_no':final['inv_no'],
                                 'type':final['type'],
                                 'rate':temp['temp_rate'],
                                 'amt':temp['temp_amt'],
                                 'qty':temp['temp_qty'],
                                 'uos':final['uos'],
                               }
                    self.list_sale.append(sale_dict)
                else:
                    sale_dict={
                                 'date':final['date'],
                                 'inv_no':final['inv_no'],
                                 'type':final['type'],
                                 'rate':temp['temp_rate'],
                                 'amt':final['qty']*temp['temp_rate'],
                                 'qty':final['qty'],
                                 'uos':final['uos'],
                               }
                    self.list_sale.append(sale_dict)
                if form['method']=='fifo':
                    if self.test1 !=[]:
                        if (final['qty'] > self.test1[0]['qty']) or (final['qty'] == self.test1[0]['qty']):
                            self.test1.remove(self.test1[0]) 
                        else: 
                            self.test1[0]['qty']-=final['qty']
                            self.test1[0]['amt']=self.test1[0]['qty']*self.test1[0]['rate']       
                if form['method']=='lifo':
                    if self.test1 !=[]:
                        if (final['qty'] > self.test1[-1]['qty']) or (final['qty'] == self.test1[-1]['qty']):
                            self.test1.pop(-1)
                        else: 
                            self.test1[-1]['qty']-=final['qty']
                            self.test1[-1]['amt']=self.test1[-1]['qty']*self.test1[-1]['rate']
                temp1['temp_qty']=final['qty']-temp['temp_qty']
                if temp1['temp_qty'] > 0:
                    if form['method']=='fifo':
                        if self.test1 !=[]:
                            temp2['temp_qty']=self.test1[0]['qty']
                            temp2['temp_rate']=self.test1[0]['rate']  
                            temp2['temp_amt']=self.test1[0]['amt']
                            if (temp2['temp_qty']-temp1['temp_qty'])>0: 
                                self.test1[0]['qty']-=temp1['temp_qty']
                                self.test1[0]['amt']=(self.test1[0]['qty']*self.test1[0]['rate'])
                            else:
                                while(temp1['temp_qty']!=0):
                                    if self.test1==[]:
                                        print "!!!!!!!!!stock inward List is empty!!!!!!!!!"
                                        break
                                    temp['temp_qty']=self.test1[0]['qty']
                                    temp['temp_rate']=self.test1[0]['rate']  
                                    temp['temp_amt']=self.test1[0]['amt']
                                    
                                    temp2['temp_qty']=self.test1[0]['qty']
                                    temp2['temp_rate']=self.test1[0]['rate']  
                                    temp2['temp_amt']=self.test1[0]['amt']
                                    
                                    if temp2['temp_qty'] < temp1['temp_qty']:
                                        self.test1.pop(-1)
                                        temp1['temp_qty']-=temp2['temp_qty']
                                        if temp2['temp_rate'] and (temp1['temp_qty']*temp2['temp_rate']) and temp1['temp_qty']>0:
                                            sale_dict={
                                                         'date':final['date'],
                                                         'inv_no':final['inv_no'],
                                                         'type':final['type'],
                                                         'rate':temp2['temp_rate'],
                                                         'amt':(temp1['temp_qty']*temp2['temp_rate']),
                                                         'qty':temp1['temp_qty'],
                                                         'uos':final['uos'],
                                                       }
                                            self.list_sale.append(sale_dict)
                                    else:
                                        self.test1[-1]['qty']-=temp1['temp_qty']
                                        self.test1[-1]['amt']=self.test1[0]['qty']*self.test1[0]['rate']
                                        break
                    if form['method']=='lifo':
                        if self.test1 !=[]:
                            temp2['temp_qty']=self.test1[-1]['qty']
                            temp2['temp_rate']=self.test1[-1]['rate']  
                            temp2['temp_amt']=self.test1[-1]['amt']
                            
                            if (temp2['temp_qty']-temp1['temp_qty'])>0: 
                                self.test1[-1]['qty']-=temp1['temp_qty']
                                self.test1[-1]['amt']=(self.test1[-1]['qty']*self.test1[-1]['rate'])
                            else:
                                while(temp1['temp_qty']!=0):
                                    if self.test1==[]:
                                        print "!!!!!!!!!stock inward List is empty!!!!!!!!!"
                                        break
                                    temp['temp_qty']=self.test1[-1]['qty']
                                    temp['temp_rate']=self.test1[-1]['rate']  
                                    temp['temp_amt']=self.test1[-1]['amt']
                                    
                                    temp2['temp_qty']=self.test1[-1]['qty']
                                    temp2['temp_rate']=self.test1[-1]['rate']  
                                    temp2['temp_amt']=self.test1[-1]['amt']
                                    
                                    if temp2['temp_qty'] < temp1['temp_qty']:
                                        self.test1.pop(-1)
                                        temp1['temp_qty']-=temp2['temp_qty']
                                        if temp2['temp_rate'] and (temp1['temp_qty']*temp2['temp_rate']) and temp1['temp_qty']>0:
                                            sale_dict={
                                                         'date':final['date'],
                                                         'inv_no':final['inv_no'],
                                                         'type':final['type'],
                                                         'rate':temp2['temp_rate'],
                                                         'amt':(temp1['temp_qty']*temp2['temp_rate']),
                                                         'qty':temp1['temp_qty'],
                                                         'uos':final['uos'],
                                                       }
                                            self.list_sale.append(sale_dict)
                                    else:
                                        self.test1[-1]['qty']-=temp1['temp_qty']
                                        self.test1[-1]['amt']=self.test1[-1]['qty']*self.test1[-1]['rate']
                                        break
                    if temp2['temp_rate'] and (temp1['temp_qty']*temp2['temp_rate']) and temp1['temp_qty']>0:
                        sale_dict={
                                     'date':final['date'],
                                     'inv_no':final['inv_no'],
                                     'type':final['type'],
                                     'rate':temp2['temp_rate'],
                                     'amt':(temp1['temp_qty']*temp2['temp_rate']),
                                     'qty':temp1['temp_qty'],
                                     'uos':final['uos'],
                                   }
                        self.list_sale.append(sale_dict)
                    if temp1['temp_qty']<0:
                        temp1['temp_qty']*=-1
                    self.p_qty -= (temp['temp_qty']+temp1['temp_qty'])
                    self.p_amt  -=((temp['temp_qty']*temp['temp_rate'])+(temp1['temp_qty']*temp2['temp_rate']))
                    t_amt1=(temp['temp_qty']*temp['temp_rate'])
                    t_amt2=(temp1['temp_qty']*temp2['temp_rate'])
                    if (t_amt1+t_amt2)>0.0:
                        diff=final['amt']-(t_amt1+t_amt2)
                        res['gp']=str('%.2f' %((diff/(t_amt1+t_amt2))*100)) + "%"
                    else:
                        res['gp']='0.0%'
                else:
                    t_amt1=(final['qty']*temp['temp_rate'])
                    diff=final['amt']-t_amt1
                    t_amt2='%.2f' %((diff/t_amt1)*100)
                    res['gp']=str(t_amt2)+"%"
                    self.p_qty-=final['qty']
                    self.p_amt-=final['amt']    
                if self.p_qty > 0:  
                    res['bal_qty']=self.p_qty
                    res['bal_rate']=(self.p_amt/self.p_qty)
                    res['bal_amt']=self.p_amt 
                else:
                    res['bal_qty']=0
                    res['bal_rate']=0.0
                    res['bal_amt']=0.0                
        result.append(res)
        return result
   
    def get_product_line(self,form):
        final_result=[]
        done=[]
        res={}
        final=[]
        temp=[]
        temp_dict={}
        line_prod_ids=[]
        type_list=['purchase','sale']
        jnl_ids=self.pool.get('account.journal').search(self.cr, self.uid, [('type','in',type_list)])
        move_line_ids=self.pool.get('account.move').search(self.cr, self.uid, [('journal_id','in',jnl_ids)])
        comp_ids=[]
        child_ids=pooler.get_pool(self.cr.dbname).get('res.company')._get_company_children(self.cr, self.uid,form['company_id'])
        if child_ids:
            comp_ids = child_ids
        else:
            comp_ids.append(form['company_id'])
        inv_ids=self.pool.get('account.invoice').search(self.cr, self.uid, [('move_id','in',move_line_ids),('account_id.company_id','in',comp_ids)])
        inv_line_ids=self.pool.get('account.invoice.line').search(self.cr, self.uid, [('invoice_id','in',inv_ids)])
        inv_line_obj=self.pool.get('account.invoice.line').browse(self.cr, self.uid, inv_line_ids)
        if form['all']== 1:
            final_result=self.get_line_detail(inv_line_obj,form)
        else:
            final_result=self.get_line_detail(inv_line_obj,form)
        for inv_line in inv_line_obj:
            if inv_line.product_id and inv_line.product_id.id not in done:
                done.append(inv_line.product_id.id)
                line_prod_ids.append(inv_line.product_id.id)
        prod_ids=self.pool.get('product.product').search(self.cr, self.uid, [('id','in',line_prod_ids)])
        prod_obj=self.pool.get('product.product').browse(self.cr, self.uid, prod_ids)
        for prod in prod_obj:
            temp=[]
            res={}
            res['name']=prod.name
            for fr in final_result:
                temp_dict={}
                if prod.name == fr['name']:
                    temp_dict['list']={
                                 'date':fr['date'],
                                 'latest_date':fr['latest_date'],
                                 'inv_no':fr['inv_no'],
                                 'type':fr['type'],
                                 'rate':fr['rate'],
                                 'amt':fr['amt'],
                                 'qty':fr['qty'],
                                 'uos':fr['uos'],
                                 }
                    temp.append(temp_dict)
            t_1=[]
            for t in temp:
              t_1.append(t['list'])  
            res['line']=t_1
            if res['line'] != []:
                final.append(res)
        return final
    
    def sortDictBy(self,list, key):
        nlist = map(lambda x, key=key: (x[key], x), list)
        nlist.sort()
        return map(lambda (key, x): x, nlist)
    
    def get_line(self,obj):
        result=self.sortDictBy(obj['line'],"latest_date")
        return result
    
    def get_line_detail(self,inv_line_obj,form):
        test={}
        final_result1=[]
        final_list=[]
        p_list=[]
        if form['all']== 1:
            for inv_l in inv_line_obj:
                test={}
                if inv_l.product_id:
                    if inv_l.invoice_id.date_invoice >= form['date1'] and inv_l.invoice_id.date_invoice <= form['date2']:
                        if inv_l.invoice_id.type == 'in_invoice' or inv_l.invoice_id.type == 'in_refund':
                            test['type']='inward'
                        if inv_l.invoice_id.type == 'out_invoice' or inv_l.invoice_id.type == 'out_refund':
                            test['type']='outward'
                        test['date']=inv_l.invoice_id.date_invoice
                        test['latest_date']=inv_l.invoice_id.latest_date
                        test['inv_no']=inv_l.invoice_id.number              
                        test['name']=inv_l.product_id.name
                        test['rate']=inv_l.exise_amt
                        test['amt']=(inv_l.exise_amt*inv_l.quantity)
                        test['qty']=inv_l.quantity
                        if inv_l.uos_id:
                            test['uos']=inv_l.uos_id.name
                        else:
                            test['uos']=''
                        final_result1.append(test)
        else:
            prod_obj=self.pool.get('product.product').browse(self.cr, self.uid,form['products'][0][2])
            for prod in prod_obj:
                p_list.append(prod.name)
            for inv_l in inv_line_obj:
                test={}
                if inv_l.product_id and (inv_l.product_id.name in p_list):
                    if inv_l.invoice_id.date_invoice >= form['date1'] and inv_l.invoice_id.date_invoice <= form['date2']:
                        if inv_l.invoice_id.type == 'in_invoice' or inv_l.invoice_id.type == 'in_refund':
                            test['type']='inward'
                        if inv_l.invoice_id.type == 'out_invoice' or inv_l.invoice_id.type == 'out_refund':
                            test['type']='outward'
                        test['date']=inv_l.invoice_id.date_invoice
                        test['latest_date']=inv_l.invoice_id.latest_date
                        test['inv_no']=inv_l.invoice_id.number              
                        test['name']=inv_l.product_id.name
                        test['rate']=inv_l.exise_amt
                        test['amt']=(inv_l.exise_amt*inv_l.quantity)
                        test['qty']=inv_l.quantity
                        if inv_l.uos_id:
                            test['uos']=inv_l.uos_id.name
                        else:
                            test['uos']=''
                        final_result1.append(test)
        return final_result1
report_sxw.report_sxw('report.stock.summary.prod.vice.report', 'account.move.line',
        'account_stock/report/report_stock_summary_product_vice.rml',parser=report_stock_summary_product_vice,
        header=False)