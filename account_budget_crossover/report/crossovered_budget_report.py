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

import time
import pooler
from report import report_sxw
import datetime
import operator
import osv

class budget_report(report_sxw.rml_parse):
	def __init__(self, cr, uid, name, context):
		super(budget_report, self).__init__(cr, uid, name, context)
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

		budgets = self.pool.get('crossovered.budget').browse(self.cr, self.uid, [object.id], self.context.copy())

		for budget_id in budgets:
			res={}
			budget_lines=[]

			d_from=form['date_from']
			d_to=form['date_to']

			query="select id from crossovered_budget_lines where crossovered_budget_id = '"+ str(budget_id.id) + "' AND '"+ str(d_from) +"'<=date_from AND date_from<date_to AND date_to<= '"+ str(d_to) +"'"
			self.cr.execute(query)
			budget_line_ids=self.cr.fetchall()

			if not budget_line_ids:
				return []

			budget_lines=[x[0] for x in budget_line_ids]
			bd_ids = ','.join([str(x) for x in budget_lines])

			self.cr.execute('select distinct(analytic_account_id) from crossovered_budget_lines where id in (%s)'%(bd_ids))
			an_ids=self.cr.fetchall()

			for i in range(0,len(an_ids)):

				analytic_name=self.pool.get('account.analytic.account').browse(self.cr, self.uid,[an_ids[i][0]])
				res={
			 		'name':analytic_name[0].name,
			 		'status':1,
			 		'theo':0.00,
			 		'pln':0.00,
			 		'prac':0.00,
			 		'perc':0.00
				}
				result.append(res)

				line_ids = self.pool.get('crossovered.budget.lines').search(self.cr, self.uid, [('id', 'in', budget_lines),('analytic_account_id','=',an_ids[i][0])])

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
					if form['report']=='analytic-full':
						result.append(res1)

				if tot_theo==0.00:
					tot_perc=0.00
				else:
					tot_perc=float(tot_prac /tot_theo)*100

				if form['report']=='analytic-full':
					result[-(len(line_id) +1)]['theo']=tot_theo
					tot['theo'] +=tot_theo
					result[-(len(line_id) +1)]['pln']=tot_pln
					tot['pln'] +=tot_pln
					result[-(len(line_id) +1)]['prac']=tot_prac
					tot['prac'] +=tot_prac
					result[-(len(line_id) +1)]['perc']=tot_perc
				else:
					result[-1]['theo']=tot_theo
					tot['theo'] +=tot_theo
					result[-1]['pln']=tot_pln
					tot['pln'] +=tot_pln
					result[-1]['prac']=tot_prac
					tot['prac'] +=tot_prac
					result[-1]['perc']=tot_perc
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

report_sxw.report_sxw('report.crossovered.budget.report', 'crossovered.budget', 'addons/account_budget_crossover/report/crossovered_budget_report.rml',parser=budget_report,header=False)

