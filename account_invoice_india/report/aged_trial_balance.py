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

class aged_trial_report1(report_sxw.rml_parse):
	def __init__(self, cr, uid, name, context):
		super(aged_trial_report1, self).__init__(cr, uid, name, context)
		self.localcontext.update({
			'time': time,
			'get_lines': self._get_lines,
			'get_total': self._get_total,
			'get_before': self._get_before,
			'get_for_period': self._get_for_period,
			'get_company': self._get_company,
			'get_currency': self._get_currency,
		})
		self.period_total = {}
	def _add_header(self, node):
		return True

	def _get_lines(self, form):
		res = []
		account_move_line_obj = pooler.get_pool(self.cr.dbname).get('account.move.line')
		line_query = account_move_line_obj._query_get(self.cr, self.uid, obj='line',
				context={'fiscalyear': form['fiscalyear']})
		self.cr.execute("SELECT DISTINCT res_partner.id AS id, " \
					"res_partner.name AS name " \
				"FROM res_partner, account_move_line AS line, account_account " \
				"WHERE (line.account_id=account_account.id) " \
				"AND (res_partner.id in (" + ",".join(map(str, form['partners'][0][2])) +")) "
					"AND (line.reconcile_id IS NULL) " \
					"AND (line.partner_id=res_partner.id) " \
					"AND " + line_query + " " \
					"AND (account_account.company_id = %d) " \
					"AND account_account.active " \
				"ORDER BY res_partner.name", (form['company_id'],))
		partners = self.cr.dictfetchall()
		for partner in partners:
			values = {}
			self.cr.execute("SELECT SUM(debit-credit) " \
					"FROM account_move_line AS line, account_account " \
					"WHERE (line.account_id=account_account.id) " \
						"AND (account_account.type IN ('payable','receivable')) " \
						"AND (date < %s) AND (partner_id=%d) " \
						"AND (reconcile_id IS NULL) " \
						"AND " + line_query + " " \
						"AND (account_account.company_id = %d) " \
						"AND account_account.active",
						(form['0']['start'], partner['id'], form['company_id']))
			before = self.cr.fetchone()
			values['before'] = before and before[0] or ""
			for i in range(5):
				self.period_total[str(i)] = 0.0
				self.cr.execute("SELECT SUM(debit-credit) " \
						"FROM account_move_line AS line, account_account " \
						"WHERE (line.account_id=account_account.id) " \
							"AND (account_account.type IN ('payable','receivable')) " \
							"AND (date >= %s) AND (date <= %s) " \
							"AND (partner_id = %d) " \
							"AND (reconcile_id IS NULL) " \
							"AND " + line_query + " " \
							"AND (account_account.company_id = %d) " \
							"AND account_account.active",
							(form[str(i)]['start'], form[str(i)]['stop'],
								partner['id'], form['company_id']))
				during = self.cr.fetchone()
				
				values[str(i)] = during and during[0] or ""

			self.cr.execute("SELECT SUM(debit-credit) " \
					"FROM account_move_line AS line, account_account " \
					"WHERE (line.account_id = account_account.id) " \
						"AND (account_account.type IN ('payable','receivable')) " \
						"AND (partner_id = %d) " \
						"AND (reconcile_id IS NULL) " \
						"AND " + line_query + " " \
						"AND (account_account.company_id = %d) " \
						"AND account_account.active",
						(partner['id'], form['company_id']))
			total = self.cr.fetchone()
			values['total'] = total and total[0] or 0.0
			values['name'] = partner['name']
			t = 0.0
			for i in range(5)+['before']:
				t+= float(values.get(str(i), 0.0) or 0.0)
			if values['total']:
				res.append(values)
		total = 0.0
		totals = {}
		for r in res:
			total += float(r['total'] or 0.0)
			for i in range(5)+['before']:
				totals.setdefault(str(i), 0.0)
				totals[str(i)] += float(r[str(i)] or 0.0)
		return res
	
	def _get_total(self, fiscalyear, partner, company_id):
		account_move_line_obj = pooler.get_pool(self.cr.dbname).get('account.move.line')
		line_query = account_move_line_obj._query_get(self.cr, self.uid, obj='line',
				context={'fiscalyear': fiscalyear})
		partners = partner[0][2]
		period_total = 0.0
		for partner in partners:
			self.cr.execute("SELECT SUM(debit - credit) " \
					"FROM account_move_line AS line, account_account " \
					"WHERE (line.account_id = account_account.id) " \
						"AND (account_account.type IN ('payable', 'receivable')) "\
						"AND reconcile_id IS NULL " \
						"AND (partner_id = %d )" \
						"AND " + line_query + " " \
						"AND (account_account.company_id = %d) " \
						"AND account_account.active",
						(partner,company_id))
			result = self.cr.fetchone()
			if result[0] != None:
				period_total +=result[0]
		return period_total or 0.0
	
	def _get_before(self, date, fiscalyear, partner, company_id):
		account_move_line_obj = pooler.get_pool(self.cr.dbname).get('account.move.line')
		line_query = account_move_line_obj._query_get(self.cr, self.uid, obj='line',
				context={'fiscalyear': fiscalyear})
		partners = partner[0][2]
		period_total = 0.0
		for partner in partners:
			self.cr.execute("SELECT SUM(debit - credit) " \
					"FROM account_move_line AS line, account_account " \
					"WHERE (line.account_id = account_account.id) " \
						"AND (account_account.type IN ('payable', 'receivable')) " \
						"AND reconcile_id IS NULL " \
						"AND (date < %s) " \
						"AND (partner_id = %d )" \
						"AND " + line_query + " " \
						"AND (account_account.company_id = %d) " \
						"AND account_account.active",
						(date,partner, company_id))
			result = self.cr.fetchone()
			if result[0] != None:
				period_total +=result[0]
		return period_total or 0.0

	def _get_for_period(self, period, fiscalyear, partner, company_id):
		account_move_line_obj = pooler.get_pool(self.cr.dbname).get('account.move.line')
		line_query = account_move_line_obj._query_get(self.cr, self.uid, obj='line',
				context={'fiscalyear': fiscalyear})
		partners = partner[0][2]
		period_total = 0.0
		for partner in partners:
			self.cr.execute("SELECT SUM(debit - credit) " \
					"FROM account_move_line AS line, account_account " \
					"WHERE (line.account_id = account_account.id) " \
						"AND (account_account.type IN ('payable', 'receivable')) " \
						"AND reconcile_id IS NULL " \
						"AND (date >= %s) " \
						"AND (date <= %s) " \
						"AND (partner_id = %d )" \
						"AND " + line_query + " " \
						"AND (account_account.company_id = %d) " \
						"AND account_account.active",
						(period['start'], period['stop'], partner, company_id))
			result = self.cr.fetchone()
			if result[0] != None:
				period_total +=result[0]
		return period_total or 0.0

	def _get_company(self, form):
		return pooler.get_pool(self.cr.dbname).get('res.company').browse(self.cr, self.uid, form['company_id']).name

	def _get_currency(self, form):
		return pooler.get_pool(self.cr.dbname).get('res.company').browse(self.cr, self.uid, form['company_id']).currency_id.name

report_sxw.report_sxw(
	'report.account.aged.trial.balance1',
	'res.partner',
	'addons/account_invoice_india/report/aged_trial_balance.rml',
	parser=aged_trial_report1, header=False)
