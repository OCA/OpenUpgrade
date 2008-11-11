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

class report_pl_account_tiny(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(report_pl_account_tiny, self).__init__(cr, uid, name, context)
        self.total=0.0
        self.result=[]
        self.localcontext.update({
            'time': time,
            'get_tplines': self._get_tplines,
            'get_lines': self._get_lines,
            'get_total': self._get_total,
           
        })
        
    def _get_tplines(self,form,ids={},level=1):
        if not ids:
            ids = self.ids
        if not ids:
            return []
        res={}
        self.result=[]
        dict=[]
        res1={}
        accounts = self.pool.get('account.account').browse(self.cr, self.uid, ids)
        for account in accounts:
                if account.code=='AC0':
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
        for d in dict:
            self.total+=d['progress']
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
        res={
             'np':'',
             'val':0.0
             }
        if self.total<0:
            res['np']="Net Profit:"
            res['val']=self.total
        else:
            res['np']="Net Loss:"
            res['val']=self.total
        return res or ''    
        
report_sxw.report_sxw(
    'report.report.pl.account.tiny',
    'account.account',
    'addons/account_indian_report/report/report_pl_account_tiny.rml',
    parser=report_pl_account_tiny, header=False)
