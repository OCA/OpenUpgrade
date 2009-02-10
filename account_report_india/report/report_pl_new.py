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

class report_pl_new(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(report_pl_new, self).__init__(cr, uid, name, context)
        self.res_pl ={}
        self.final=[]
        self.localcontext.update( {
            'time': time,
            'get_lines' : self.get_lines,
            'get_data': self.get_data,
            'final_result' : self.final_result,
            'get_acc_obj':self.get_acc_obj,
        })
        self.context = context
        
    def final_result(self):
        return self.res_pl

    def get_data(self,obj):
        final=[]
        tot_level0=0.00
        tot_level1=0.00
        tot_level2=0.00
        temp_total=0.0
        if obj.group_type == 'pl_accounts_group':
            seq_list=['Sales Account','Goods Given Account','Opening Stock','Purchase','Direct Expenses','Direct Incomes','Indirect Incomes','Indirect Expenses']
            cs_list=['Opening Stock','Purchase','Direct Expenses']
            np_list_acc=['Direct Incomes','Indirect Incomes','Indirect Expenses']
            acc_objs=[]
            result=[]
            res={}
            acc_objs=self.get_acc_obj(obj.acc_detail)
            for aobj in acc_objs:
                res={}
                if aobj.level == 0:
                    result.append(aobj)
            for seq in seq_list:
                for r in result:
                    if r.name == seq:
                        final.append(r)
                        break
            result=[]
            for aobj in final:
                res={}
                if aobj.name == 'Sales Account' or  aobj.name == 'Goods Given Account':
                    res['name']=aobj.name
                    res['balance']=aobj.balance
                    res['type']=aobj.type
                    res['level']=aobj.level
                    res['outer']='1'
                    if res['balance'] <  0.0:
                        res['balance'] *= -1
                    tot_level0 += res['balance']
                    result.append(res)
                    if aobj.name == 'Goods Given Account':
                        res={}
                        res['name']='Less' +':-' +'Cost of Sale'
                        res['balance']=0.0
                        res['type']=aobj.type
                        res['level']=aobj.level
                        res['outer']='0'
                        result.append(res)
                if aobj.name in cs_list:
                    if aobj.name == 'Opening Stock' or aobj.name == 'Purchase':
                        res['name']="   " + aobj.name
                        res['balance']=aobj.balance
                        res['type']=aobj.type
                        res['level']=aobj.level
                        res['outer']='-1'
                        if res['balance'] <  0.0:
                            res['balance'] *= -1
                        tot_level1 += res['balance']
                        tot_level2 += res['balance']
                        result.append(res)
                        
                        if aobj.name == 'Purchase':
                            for r in result:
                                if r['name'] == 'Less:-Cost of Sale':
                                    r['balance'] += tot_level2
                    if aobj.name == 'Direct Expenses':
                        res={}
                        res['name']="   " + aobj.name
                        res['balance']=aobj.balance
                        res['type']=aobj.type
                        res['level']=aobj.level
                        res['outer']='0'
                        if res['balance'] <  0.0:
                            res['balance'] *= -1
                        tot_level2 += res['balance']
                        result.append(res)
                        
                        res={}
                        res['name']="Total _________________________________________________________________________________________________________"
                        res['balance']=tot_level2
                        res['type']=aobj.type
                        res['level']=aobj.level
                        res['outer']='1'
                        if res['balance'] <  0.0:
                            res['balance'] *= -1
                        result.append(res)
                        
                        res={}
                        if tot_level0 > tot_level2:
                            res['name']='Gross Profit'
                            res['balance']=tot_level0 - tot_level2
                            res['type']=aobj.type
                            res['level']=aobj.level
                            res['outer']='1'
                            tot_level0= res['balance']
                            result.append(res)
                        else:
                            res['name']='Gross Loss'
                            res['balance']=tot_level0 - tot_level2
                            res['type']=aobj.type
                            res['level']=aobj.level
                            res['outer']='1'
                            tot_level0= res['balance']
                            result.append(res)
                            
                if aobj.name in np_list_acc:
                   res={}
                   if  aobj.name == 'Direct Incomes' or aobj.name == 'Indirect Incomes':
                        res['name']="Add" +':-' + aobj.name
                        res['balance']=aobj.balance
                        res['type']=aobj.type
                        res['level']=aobj.level
                        res['outer']='0'
                        if res['balance'] <  0.0:
                            res['balance'] *= -1
                        temp_total +=res['balance']
                        tot_level2 += res['balance']
                        tot_level0 += res['balance']
                        result.append(res)
                        if  aobj.name == 'Indirect Incomes':
                            res={}
                            res['name']="Total _________________________________________________________________________________________________________"
                            res['balance']=temp_total
                            res['type']=aobj.type
                            res['level']=aobj.level
                            res['outer']='1'
                            if res['balance'] <  0.0:
                                res['balance'] *= -1
                            result.append(res)
                   if  aobj.name == 'Indirect Expenses':
                        res={}
                        res['name']="Final Total"
                        res['balance']=tot_level0
                        res['type']=aobj.type
                        res['level']=aobj.level
                        res['outer']='1'
                        if res['balance'] <  0.0:
                            res['balance'] *= -1
                        result.append(res)

                        res={}
                        res['name']= "Less" +':-' + aobj.name
                        res['balance']=aobj.balance
                        res['type']=aobj.type
                        res['level']=aobj.level
                        res['outer']='1'
                        if tot_level0 < res['balance']:
                            self.res_pl['type']='Net Loss'
                            self.res_pl['balance']=(res['balance'] - tot_level0)
                        else:
                            self.res_pl['type']='Net Profit'
                            self.res_pl['balance']=(tot_level0 - res['balance'])   
                        result.append(res)
        self.final = result
        return None
            
    def get_lines(self):
        return self.final
    
    def get_acc_obj(self,obj_list):
        done=[]
        result=[]
        for obj_acc in obj_list:
            if obj_acc.name not in done:
                done.append(obj_acc.name)
                result.append(obj_acc)       
        return result
    
report_sxw.report_sxw('report.pl.new', 'account.report.india',
    'addons/account_report_india/report/report_pl_new.rml',parser=report_pl_new,
    header=False)

