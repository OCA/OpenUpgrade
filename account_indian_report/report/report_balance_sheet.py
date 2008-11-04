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
import time
import pooler
from report import report_sxw
from account import *

class report_balance_sheet(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(report_balance_sheet, self).__init__(cr, uid, name, context)
        self.debittot=0.0
        self.credittot=0.0
        self.pl=0.00
        self.result=[]
        self.localcontext.update({
            'time': time,
            'get_tplines': self._get_tplines,
            'get_lines': self._get_lines,
            'get_total': self._get_total,
            'get_pl': self._get_pl,    
        })    
    def _get_tplines(self,form,ids={},level=1):
        if not ids:
            ids = self.ids
        if not ids:
            return []
        res={}
        self.result=[]
        dict=[]
        accounts = self.pool.get('account.account').browse(self.cr, self.uid, ids)
        for account in accounts:
                if account.code=='AC1':
                    continue
                res['id']=account.id
                res['code']=account.code
                res['name']=account.name
                res['debit']=account.debit
                res['credit']=account.credit
                res['progress']=account.balance
                res['level']=level
                self.result.append(res)
                res={}
                if account.child_id:
                        self.result[-1]['status']=1          
                        for x in account.child_id:
                            self.result +=self._get_tplines(form,[x.id],level+1)
                else:
                    self.result[-1]['status']=0           
                dict+=self._get_lines(form,account)
        return self.result
    def _get_lines(self,form,obj):
        res={}
        account = self.pool.get('account.account').browse(self.cr, self.uid,obj['id'])
        query = self.pool.get('account.move.line')._query_get(self.cr, self.uid,context={'fiscalyear': form['fiscalyear'],'periods':form['periods'][0][2]})            
        self.cr.execute("SELECT l.date, j.name as jname,l.name as lname, l.debit, l.credit "\
                    "FROM account_move_line l, account_journal j "\
                    "WHERE l.journal_id = j.id "\
                        "AND account_id = %d AND "+query+" "\
                    "ORDER by l.id", (account.id,))
        res=self.cr.dictfetchall()
        sum = 0.0    
        for l in res:
            sum += l['debit'] - l ['credit']
            l['progress'] = sum
            self.debittot+=l['debit']
            self.credittot+=l['credit']
        if not res and form['empty_account']==0:
             for el in self.result:
               if el['code'] == obj['code']:
                   if el['status']==0:
                       self.result.remove(el)
                   else:
                       if el['progress']==0.00 and el['code'] <> '0':
                           self.result.remove(el)
        return res or ''        
    def _get_total(self):
        res1={}
        res={
             'debittot':0.0,
             'credittot':0.0
             }
        if self.debittot>self.credittot:
            res['debittot']=self.debittot/2
            res['credittot']=self.credittot/2+self.pl
        else:
            res['debittot']=float(self.debittot/2)+self.pl
            res['credittot']=self.credittot/2
        return res or ''   
    def _get_pl(self):
        res={}
        res2={}
        self.cr.execute('select code,name from account_account where name='"'Profit and Loss'"'')
        res2=self.cr.dictfetchone()
        self.cr.execute('select sum(al.debit),sum(al.credit) from account_move_line al,account_account a where a.code like '"'AC1%'"' and a.id=al.account_id')
        res1=self.cr.fetchone()
        if res1[0] is None  or res1[1] is None:
                self.pl=0.00
        if res1[0]>res1[1]:
            self.pl=res1[0]-res1[1];
        else:
            self.pl=res1[1]-res1[0]; 
        
        if self.debittot>self.credittot:
            res['date1']=time.strftime('%Y-%m-%d')
            res['code1']=res2['code']
            res['name1']=res2['name']
            res['balance1']=self.pl
            res['date']=''
            res['code']=''
            res['name']=''
            res['balance']=''
        else: 
            res['date1']=''
            res['code1']=''
            res['name1']=''
            res['balance1']=''
            res['code']=res2['code']
            res['name']=res2['name']
            res['balance']=self.pl
            res['date']=time.strftime('%Y-%m-%d')
       
        return [res]  
report_sxw.report_sxw(
    'report.report.balance.sheet',
    'account.account',
    'addons/account_indian_report/report/report_in_balance_sheet.rml',
    parser=report_balance_sheet, header=False)
