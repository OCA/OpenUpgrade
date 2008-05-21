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
        accounts = self.pool.get('account.analytic.account').browse(self.cr, self.uid, [object.id], self.context.copy())

#        if form['date_from']<=accounts[0].date_start< accounts[0].date<=form['date_to']:
#            go=1 # does nothing just carry on.
#        else:
#            return [] # stops calculations.displays nothing

        for account_id in accounts:
            res={}
            budget_lines=[]

            for line in account_id.crossovered_budget_line:
                budget_lines.append(line.id)

            bd_lines_ids = ','.join([str(x) for x in budget_lines])

            d_from=form['date_from']
            d_to=form['date_to']

            query="select id from crossovered_budget_lines where id in ("+ str(bd_lines_ids) + ") AND '"+ str(d_from) +"'<=date_from AND date_from<date_to AND date_to<= '"+ str(d_to) +"'"

            self.cr.execute(query)
            budget_line_ids=self.cr.fetchall()

            if not budget_line_ids:
                return []

            budget_lines=[x[0] for x in budget_line_ids]

            bd_ids = ','.join([str(x) for x in budget_lines])

            self.cr.execute('select distinct(crossovered_budget_id) from crossovered_budget_lines where id in (%s)'%(bd_ids))
            budget_ids=self.cr.fetchall()

            for i in range(0,len(budget_ids)):

                budget_name=self.pool.get('crossovered.budget').browse(self.cr, self.uid,[budget_ids[i][0]])
                res={
                     'id':'-1',
                     'name':budget_name[0].name,
                     'status':1,
                     'theo':0.00,
                     'pln':0.00,
                     'prac':0.00,
                     'perc':0.00
                }
                result.append(res)

                line_ids = self.pool.get('crossovered.budget.lines').search(self.cr, self.uid, [('id', 'in', budget_lines),('crossovered_budget_id','=',budget_ids[i][0])])
                line_id = self.pool.get('crossovered.budget.lines').browse(self.cr,self.uid,line_ids)
                tot_theo=tot_pln=tot_prac=tot_perc=0

                done_budget=[]
                for line in line_id:

                    if line.general_budget_id.id in done_budget:

                        for record in result:
                            if record['id']==line.general_budget_id.id:

                                record['theo'] +=line.theoritical_amount
                                record['pln'] +=line.planned_amount
                                record['prac'] +=line.practical_amount
                                record['perc'] +=line.percentage
                                tot_theo += line.theoritical_amount
                                tot_pln +=line.planned_amount
                                tot_prac +=line.practical_amount
                                tot_perc +=line.percentage
                    else:

                        res1={
                             'id':line.general_budget_id.id,
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
                        done_budget.append(line.general_budget_id.id)


                if tot_theo==0.00:
                    tot_perc=0.00
                else:
                    tot_perc=float(tot_prac /tot_theo)*100

                result[-(len(done_budget) +1)]['theo']=tot_theo
                tot['theo'] +=tot_theo
                result[-(len(done_budget) +1)]['pln']=tot_pln
                tot['pln'] +=tot_pln
                result[-(len(done_budget) +1)]['prac']=tot_prac
                tot['prac'] +=tot_prac
                result[-(len(done_budget) +1)]['perc']=tot_perc

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

report_sxw.report_sxw('report.account.analytic.account.budget', 'account.analytic.account', 'addons/account_budget_crossover/report/analytic_account_budget_report.rml',parser=analytic_account_budget_report,header=False)
