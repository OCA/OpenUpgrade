import time
import pooler
from report import report_sxw
from account import *

class report_balance_sheet_tiny(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(report_balance_sheet_tiny, self).__init__(cr, uid, name, context)
        self.total=0.0
        self.result=[]
        self.localcontext.update({
            'time': time,
            'get_tplines': self._get_tplines,
            'get_lines': self._get_lines,
           
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
report_sxw.report_sxw(
    'report.report.balance.sheet.tiny',
    'account.account',
    'addons/account_indian_report/report/report_in_balance_sheet_tiny.rml',
    parser=report_balance_sheet_tiny, header=False)
