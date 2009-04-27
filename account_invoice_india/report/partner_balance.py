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

import pooler
import time
import mx.DateTime
from report import report_sxw

class partner_balance(report_sxw.rml_parse):
	def __init__(self, cr, uid, name, context):
		super(partner_balance, self).__init__(cr, uid, name, context)
		self.sum_debit = 0.0
		self.sum_credit = 0.0
		self.sum_opdebit=0.0
		self.sum_opcredit=0.0
		self.sum_cldebit=0.0
		self.sum_clcredit=0.0
		self.result=[]
		self.localcontext.update( {
			'time': time,
			'lines': self.lines,
			'cl_to_op': self.cl_to_op,
			'sum_debit': self._sum_debit,
			'sum_credit': self._sum_credit,
			'cal_res': self.cal_res,
			'sum_opdebit': self._sum_opdebit,
			'sum_opcredit': self._sum_opcredit,
			'solde_debit': self._solde_balance_debit,
			'solde_credit': self._solde_balance_credit,
			'get_company': self._get_company,
			'get_currency': self._get_currency,
		})
		
	def lines(self,form):
		self.sum_debit = 0.0
		self.sum_credit = 0.0
		self.sum_opdebit=0.0
		self.sum_opcredit=0.0
		self.sum_cldebit=0.0
		self.sum_clcredit=0.0
		p_lst=[]
		final_res=[] 
		test={}
		fiscalyear_obj =  pooler.get_pool(self.cr.dbname).get('account.fiscalyear')
		context={'fiscalyear': self.datas['form']['fiscalyear']}
		year_start_date = fiscalyear_obj.browse(self.cr, self.uid, context['fiscalyear']).date_start
		start_date=fiscalyear_obj.browse(self.cr, self.uid, context['fiscalyear'])
		year_start_date = start_date.date_start
		end_date=fiscalyear_obj.browse(self.cr, self.uid, context['fiscalyear'] )
		year_end_date = end_date.date_stop 
		if self.datas['form']['date1'] >= year_start_date and self.datas['form']['date2'] <= year_end_date:
			self.ACCOUNT_TYPE = "('payable','receivable')"
			self.cr.execute("SELECT a.id " \
			        "FROM account_account a " \
			        "LEFT JOIN account_account_type t " \
			            "ON (a.type = t.code) " \
			        "WHERE a.company_id = %s " \
			            "AND a.type IN " + self.ACCOUNT_TYPE + " " \
			            "AND a.active", (form['company_id'],))
#			self.cr.execute('SELECT a.id ' \
#				'FROM account_account a ' \
#					'WHERE a.company_id = %d ' \
#					'AND a.active', (form['company_id'],))
			account_ids = ','.join([str(a) for (a,) in self.cr.fetchall()])
			partner_id = ','.join([str(a) for a in form['partners'][0][2]])
			if not partner_id or not account_ids:
				return []
			account_move_line_obj = pooler.get_pool(self.cr.dbname).get('account.move.line')
			line_query = account_move_line_obj._query_get(self.cr, self.uid, obj='l',
				context={'fiscalyear': self.datas['form']['fiscalyear']})
			self.cr.execute(
				"SELECT p.ref, p.name, " \
					"CASE WHEN j.type != 'situation' " \
						"THEN sum(debit) " \
						"ELSE 0 " \
						"END AS debit, " \
					"CASE WHEN j.type != 'situation' " \
						"THEN sum(credit) " \
						"ELSE 0 " \
						"END AS credit, " \
					"CASE WHEN j.type = 'situation' " \
						"THEN sum(debit) " \
						"ELSE 0 " \
						"END AS opdebit, " \
					"CASE WHEN j.type = 'situation' " \
						"THEN sum(credit) " \
						"ELSE 0 " \
						"END AS opcredit " \
				"FROM account_move_line l LEFT JOIN res_partner p ON (l.partner_id=p.id) LEFT JOIN account_journal j ON (j.id = l.journal_id) " \
				"WHERE partner_id IN (" + partner_id + ") " \
					"AND l.account_id IN (" + account_ids + ") " \
					"AND l.date >= %s " \
					"AND l.date <= %s " \
					"AND " + line_query + " " \
				"GROUP BY p.id, p.ref, p.name, j.type " \
				"ORDER BY p.ref, p.name ",
				(self.datas['form']['date1'], self.datas['form']['date2']))
			res = self.cr.dictfetchall()
			for l in res:
				if l['name'] not in p_lst:
					p_lst.append(l['name'])
			for p in p_lst:
				test=self.cal_res(p,res)
 				final_res.append(test) 		
 		 	if year_start_date < self.datas['form']['date1']:
 			 	p_lst1=[]
 			 	test1={}
 			 	final_res1=[]
 			 	temp_cl={}
 			 	cl_res=self.cl_to_op(year_start_date,self.datas['form']['date1'],partner_id,account_ids)
 			 	if cl_res:
	 			 	for l in cl_res:
				 		 if l['name'] not in p_lst1:
							p_lst1.append(l['name'])
					for p in p_lst1:
						test1=self.cal_res(p,cl_res)
	 					final_res1.append(test1) 
	 				for f in final_res1:
						 if ((f['debit']+f['opdebit']) - (f['credit']+f['opcredit'])) > 0.0:
								temp_cl['sdebit']=((f['debit']+f['opdebit']) - (f['credit']+f['opcredit']))
								temp_cl['scredit']=0.0		
						 else:
								temp_cl['scredit']=((f['credit']+f['opcredit']) - (f['debit']+f['opdebit']))
								temp_cl['sdebit']=0.0
						 f['opdebit']=temp_cl['sdebit']
						 f['opcredit']=temp_cl['scredit']
						 f['debit']=0.0
						 f['credit']=0.0
					final_res11=final_res1
					for fr in final_res:
						for fr1 in final_res1:
							if fr1['name'] == fr['name']:
								fr['opdebit']=fr1['opdebit']
								fr['opcredit']=fr1['opcredit']
								final_res11.remove(fr1)
							else:
							 continue
					for fr1 in final_res11:
						final_res.append(fr1)
 			for l1 in final_res:
				self.sum_opdebit += l1['opdebit']
				self.sum_opcredit += l1['opcredit']
				self.sum_debit+=l1['debit']
				self.sum_credit+=l1['credit']
				if ((l1['debit']+l1['opdebit']) - (l1['credit']+l1['opcredit'])) > 0.0:
					l1['sdebit']=((l1['debit']+l1['opdebit']) - (l1['credit']+l1['opcredit']))
					l1['scredit']=0.0
					self.sum_cldebit+=l1['sdebit']
				else:
					l1['scredit']=((l1['credit']+l1['opcredit']) - (l1['debit']+l1['opdebit']))
					l1['sdebit']=0.0
					self.sum_clcredit+=l1['scredit']
		return final_res	
	
	def cl_to_op(self,st_date,end_date,pids,accids):
		account_move_line_obj = pooler.get_pool(self.cr.dbname).get('account.move.line')
		line_query = account_move_line_obj._query_get(self.cr, self.uid, obj='l',
				context={'fiscalyear': self.datas['form']['fiscalyear']})
		self.cr.execute(
			"SELECT p.ref, p.name, " \
					"CASE WHEN j.type != 'situation' " \
						"THEN sum(debit) " \
						"ELSE 0 " \
						"END AS debit, " \
					"CASE WHEN j.type != 'situation' " \
						"THEN sum(credit) " \
						"ELSE 0 " \
						"END AS credit, " \
					"CASE WHEN j.type = 'situation' " \
						"THEN sum(debit) " \
						"ELSE 0 " \
						"END AS opdebit, " \
					"CASE WHEN j.type = 'situation' " \
						"THEN sum(credit) " \
						"ELSE 0 " \
						"END AS opcredit " \
			"FROM account_move_line l LEFT JOIN res_partner p ON (l.partner_id=p.id) LEFT JOIN account_journal j ON (j.id = l.journal_id) " \
			"WHERE partner_id IN (" + pids + ") " \
				"AND l.account_id IN (" + accids + ") " \
				"AND l.date >= %s " \
				"AND l.date <= %s " \
				"AND " + line_query + " " \
			"GROUP BY p.id, p.ref, p.name, j.type " \
			"ORDER BY p.ref, p.name ",
			(st_date, end_date))
		res = self.cr.dictfetchall()
		return res	
	
	def cal_res(self,p,res):
		temp={}
		temp['ref']=''
		temp['name']=''
		temp['debit']=0.0
		temp['credit']=0.0
		temp['opdebit']=0.0
		temp['opcredit']=0.0
		for l in res:
			if l['name'] != p:
				continue
			temp['ref']=l['ref']
			temp['name']=l['name']
			temp['debit']+=l['debit']
			temp['credit']+=l['credit']
			temp['opdebit']+=l['opdebit']
			temp['opcredit']+=l['opcredit']
		return temp
	
	def _sum_debit(self):
		return self.sum_debit or 0.0

	def _sum_credit(self):
		return self.sum_credit or 0.0
	
	def _sum_opdebit(self):
		return self.sum_opdebit or 0.0

	def _sum_opcredit(self):
		return self.sum_opcredit or 0.0

	def _solde_balance_debit(self):
		return self.sum_cldebit or 0.0
		
	def _solde_balance_credit(self):
		return self.sum_clcredit or 0.0

	def _get_company(self, form):
		return pooler.get_pool(self.cr.dbname).get('res.company').browse(self.cr, self.uid, form['company_id']).name

	def _get_currency(self, form):
		return pooler.get_pool(self.cr.dbname).get('res.company').browse(self.cr, self.uid, form['company_id']).currency_id.name

report_sxw.report_sxw('report.account.partner.balance.new', 'res.partner',
	'addons/account_invoice_india/report/partner_balance.rml',parser=partner_balance,
	header=False)

