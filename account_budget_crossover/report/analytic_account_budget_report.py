import time
import pooler
from report import report_sxw
import datetime

class analytic_account_budget_report(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(analytic_account_budget_report, self).__init__(cr, uid, name, context)
        self.localcontext.update( {
            'funct': self.funct,
            'funct_total': self.funct_total,
            'time': time,
        })
        self.context=context


    def funct(self,object,form,ids={}, done=None, level=1):

        if not ids:
            ids = self.ids

        if not ids:
            return []
        if not done:
            done={}

        global tot
        tot={
            'theo':0.00,
            'pln':0.00,
            'prac':0.00,
            'perc':0.00
        }
        result=[]
        res={}

        accounts = self.pool.get('account.analytic.account').browse(self.cr, self.uid, [object.id], self.context.copy)

        if form['date_from']<=accounts[0].date_start< accounts[0].date<=form['date_to']:
            go=1 # does nothing just carry on.
        else:
            return [] # stops calculations.displays nothing

        for account_id in accounts:
            res={}
            budget_lines = self.pool.get('crossovered.budget.lines').search(self.cr, self.uid, [('analytic_account_id', '=', account_id.id)])
            print "account lines",budget_lines
            bd_lines_ids = ','.join([str(x) for x in budget_lines])
            self.cr.execute('select distinct(crossovered_budget_id) from crossovered_budget_lines where id in (%s)'%(bd_lines_ids))
            budget_ids=self.cr.fetchall()

            print "budgets selctd are,",budget_ids
            for i in range(0,len(budget_ids)):

                budget_name=self.pool.get('crossovered.budget').browse(self.cr, self.uid,[budget_ids[i][0]])
                res={
                     'name':budget_name[0].name,
                     'status':1,
                     'theo':0.00,
                     'pln':0.00,
                     'prac':0.00,
                     'perc':0.00
                }
                result.append(res)

                line_ids = self.pool.get('crossovered.budget.lines').search(self.cr, self.uid, [('crossovered_budget_id', '=', budget_ids[i][0]),('analytic_account_id','=',account_id.id)])
                line_id = self.pool.get('crossovered.budget.lines').browse(self.cr,self.uid,line_ids)
                tot_theo=tot_pln=tot_prac=tot_perc=0

                for line in line_id:

                    res1={
                         'name':line.general_budget_id.name,
                         'status':2,
                         'theo':line.theoritical_amount,
                         'pln':line.planned_amount,
                         'prac':line.practical_amount,
                         'perc':line.percentage
                    }
                    tot_theo += line.theoritical_amount
                    tot_pln +=line.planned_amount
                    tot_prac +=line.practical_amount
                    tot_perc +=line.percentage
                    result.append(res1)

                if tot_theo==0.00:
                    tot_perc=0.00
                else:
                    tot_perc=float(tot_prac /tot_theo)*100

                result[-(len(line_id) +1)]['theo']=tot_theo
                tot['theo'] +=tot_theo
                result[-(len(line_id) +1)]['pln']=tot_pln
                tot['pln'] +=tot_pln
                result[-(len(line_id) +1)]['prac']=tot_prac
                tot['prac'] +=tot_prac
                result[-(len(line_id) +1)]['perc']=tot_perc

            if tot['theo']==0.00:
                tot['perc'] =0.00
            else:
                tot['perc']=float(tot['prac'] /tot['theo'])*100

        return result

    def funct_total(self,form):
        result=[]
        res={}

        res={
             'tot_theo':tot['theo'],
             'tot_pln':tot['pln'],
             'tot_prac':tot['prac'],
             'tot_perc':tot['perc']
        }
        result.append(res)


        return result

report_sxw.report_sxw('report.account.analytic.account.budget', 'account.analytic.account', 'addons/crossovered_budget/report/analytic_account_budget_report.rml',parser=analytic_account_budget_report,header=False)
