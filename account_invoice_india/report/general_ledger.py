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
from report import report_sxw

class GeneralLedger(report_sxw.rml_parse):
	def __init__(self, cr, uid, name, context):
		super(GeneralLedger, self).__init__(cr, uid, name, context)
		self.localcontext.update({
			'time': time,
			'lines': self.lines,
			'sum_debit_account': self._sum_debit_account,
			'sum_credit_account': self._sum_credit_account,
			'sum_debit': self._sum_debit,
			'sum_credit': self._sum_credit,
		})
		self.context = context

	def lines(self, account, form):
		datas = form
		ctx = self.context.copy()
		ctx['fiscalyear'] = form['fiscalyear']
		query = self.pool.get('account.move.line')._query_get(self.cr, self.uid, context=ctx)
		
		sSQL = "SELECT m.id as mid, l.id as lid, l.date, j.code, m.name as jv_name, p.name as pname, a.name as name, l.ref, l.name as aname, m.narration, " \
	        "l.debit, l.credit "\
		    "FROM  account_journal j, account_account a, account_move m, account_move_line l "\
	        "LEFT JOIN res_partner p " \
	        "ON (l.partner_id = p.id) " \
		    "WHERE l.journal_id = j.id AND l.account_id = a.id AND m.id = l.move_id "\
		    "AND l.date >= '" + datas['date1'] + "'"\
	        "AND l.date <= '" + datas['date2'] + "' " \
		    "AND account_id = " + str(account.id) + " AND " + query + " "\
		    "ORDER by l.date,l.move_id, pname"
		self.cr.execute(sSQL)
		res = self.cr.dictfetchall()
		if res:
			for rs in res:
				sSQL = "SELECT a.name from account_move m, account_move_line l, account_account a WHERE m.id = l.move_id AND l.account_id = a.id and m.id = %s and l.id <> %s" % (rs['mid'], rs['lid'])
				self.cr.execute(sSQL)
				namers = self.cr.dictfetchall()
				name = namers[0]['name']
				if rs['debit'] > 0:
					rs['name'] = "By " + rs['name']
					rs['jv_name'] = "Receipt"
				elif rs['credit'] > 0:
					rs['name'] = "To " + rs['name']
					rs['jv_name'] = "Payment"
		return res

	def _sum_debit_account(self, account, form):
		ctx = self.context.copy()
		ctx['fiscalyear'] = form['fiscalyear']
		#ctx['periods'] = form['periods'][0][2]
		query = self.pool.get('account.move.line')._query_get(self.cr, self.uid, context=ctx)
		self.cr.execute("SELECT sum(debit) "\
				"FROM account_move_line l "\
				"WHERE l.account_id = %s " \
				"AND l.date >= '" + form['date1'] + "' "\
                "AND l.date <= '" + form['date2'] + "' " \
                "AND " + query, (account.id,))
		return self.cr.fetchone()[0] or 0.0

	def _sum_credit_account(self, account, form):
		ctx = self.context.copy()
		ctx['fiscalyear'] = form['fiscalyear']
		#ctx['periods'] = form['periods'][0][2]
		query = self.pool.get('account.move.line')._query_get(self.cr, self.uid, context=ctx)
		self.cr.execute("SELECT sum(credit) "\
				"FROM account_move_line l "\
				"WHERE l.account_id = %s "\
				"AND l.date >= '" + form['date1'] + "' "\
                "AND l.date <= '" + form['date2'] + "' " \
                "AND " + query, (account.id,))
		return self.cr.fetchone()[0] or 0.0

	def _sum_debit(self, form):
		if not self.ids:
			return 0.0
		ctx = self.context.copy()
		ctx['fiscalyear'] = form['fiscalyear']
		#ctx['periods'] = form['periods'][0][2]
		query = self.pool.get('account.move.line')._query_get(self.cr, self.uid, context=ctx)
		self.cr.execute("SELECT sum(debit) "\
				"FROM account_move_line l "\
				"WHERE l.account_id in (" + ','.join(map(str, self.ids)) + ") " \
				"AND l.date >= '" + form['date1'] + "' "\
                "AND l.date <= '" + form['date2'] + "' " \
                "AND " + query)
		return self.cr.fetchone()[0] or 0.0

	def _sum_credit(self, form):
		if not self.ids:
			return 0.0
		ctx = self.context.copy()
		ctx['fiscalyear'] = form['fiscalyear']
		#ctx['periods'] = form['periods'][0][2]
		query = self.pool.get('account.move.line')._query_get(self.cr, self.uid, context=ctx)
		self.cr.execute("SELECT sum(credit) "\
				"FROM account_move_line l "\
				"WHERE l.account_id in (" + ','.join(map(str, self.ids)) + ") "\
				"AND l.date >= '" + form['date1'] + "' "\
                "AND l.date <= '" + form['date2'] + "' AND " + query)
		return self.cr.fetchone()[0] or 0.0

report_sxw.report_sxw(
	'report.account.general.ledger.custom.print',
	'account.account',
	'addons/account_invoice_india/report/general_ledger.rml',
	parser=GeneralLedger,
	header=False
)
