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

import time
from report import report_sxw
import rml_parse


parents = {
    'tr':1,
    'li':1,
    'story': 0,
    'section': 0
}

class account_multi_company(rml_parse.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(account_multi_company, self).__init__(cr, uid, name, context)
        self.localcontext.update({
            'time': time,
            'get_company': self.get_company,
            'get_account_detail': self.get_account_detail,
        })
        
    def get_company(self,form):
        result=[]
        res = {}
        company_ids = self.pool.get('res.company')._get_company_children(self.cr, self.uid, form['company_id'])
        comp_objs=self.pool.get('res.company').browse(self.cr,self.uid,company_ids)
        for comp_obj in comp_objs:
            res[comp_obj.name]=comp_obj.name
        result.append(res)
        return result

    def get_balance(self,move_objs):
        balance = 0.0
        debit =0.0
        credit =0.0
        for line in move_objs:
            debit += line.debit
            credit += line.credit
        balance = debit - credit
        return abs(balance)
    
    def get_account_detail(self,form,context={}):
        result=[]
        acc_ids=[]
        comp_name=[]
        res1 = {}
        r={}
        company_ids = self.pool.get('res.company')._get_company_children(self.cr, self.uid, form['company_id'])
        account_ids = self.pool.get('account.account').search(self.cr,self.uid,[('type','!=','view')])
        comp_obj = self.pool.get('res.company').browse(self.cr,self.uid,company_ids)
        for comp in comp_obj:
            self.cr.execute("select a.id as id,abs(sum(l.debit)-sum(l.credit)) as balance "\
                            "from account_account a LEFT JOIN account_move_line l on (a.id = l.account_id) "\
                            "where a.id IN (" +','.join(map(str, account_ids))+ ") AND l.company_id = %d GROUP BY a.id "%(comp.id))
            list=self.cr.dictfetchall()
            r[comp.name]=list
            comp_name.append(comp.name)
        self.cr.execute("select a.name as name, a.id as id, a.level as level, abs(sum(l.debit)-sum(l.credit)) as balance "\
                        "from account_account a LEFT JOIN account_move_line l on (a.id = l.account_id) "\
                        "where a.id IN (" +','.join(map(str, account_ids))+ ") GROUP BY a.id,a.level,a.name ")
        res_list=self.cr.dictfetchall()
        final_list = res_list
        for f in final_list:
            for c in comp_name:
                if not r[c]:
                    f[c] = 0.0
                else:    
                    value = [x['balance'] for x in r[c] if (f['id']==x['id'])]
                    f[c] = value and value[0] or 0.0
        return final_list

    def repeatIn(self, lst, name, nodes_parent=False,td=False,width=[],value=[],type=[]):
        self._node.data = ''
        node = self._find_parent(self._node, nodes_parent or parents)
        ns = node.nextSibling
        type = ['string']
        if name == 'o':
            value = lst[0]
            td = len(value)
            type = ['string'] * (td + 1)
            spcl = td
            self.c_value = value
        elif name == 'o1':
            value = lst[0]
            td = len(value) -2
            type += ['float'] * (td)
            spcl = td-2 
        else:
            return super(account_multi_company,self).repeatIn(lst, name, nodes_parent=False)    
        if not lst:
            lst.append(1)
        for ns in node.childNodes :
            if ns and ns.nodeName!='#text' and ns.tagName=='blockTable' and td :
                width_str = ns._attrs['colWidths'].nodeValue
                ns.removeAttribute('colWidths')
                for v in range(spcl):
                    width.append(int(649/spcl))
                for v in range(len(width)):
                    width_str +=',%d'%width[v]
                ns.setAttribute('colWidths',width_str)
                child_list =  ns.childNodes
                for child in child_list:
                    if child.nodeName=='tr':
                        lc = child.childNodes[1]
                        i=0
                        if name == 'o1':
                            value_new = self.c_value
                            for k,v in value_new.items():
                                value_new[k]=value[k] 
                            value = value_new
                        for v in value:
                            newnode = lc.cloneNode(1)
                            if type[i] == 'float':
                                t1="[[ '%.2f' % " + "%s['%s'] ]]"%(name,v)
                            else:
                                t1="[[ %s['%s'] ]]"%(name,v)   
                            newnode.childNodes[1].lastChild.data = t1    
                            child.appendChild(newnode)
                            newnode=False
                            i+=1
        return super(account_multi_company,self).repeatIn(lst, name, nodes_parent=False)

report_sxw.report_sxw(
    'report.account.detail',
    'account.account',
    'addons/account_multicompany/report/account_muti_company.rml',
    parser=account_multi_company
)
