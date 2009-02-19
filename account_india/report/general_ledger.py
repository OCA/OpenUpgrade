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
from report import report_sxw

class GeneralLedger(report_sxw.rml_parse):
	def __init__(self, cr, uid, name, context):
		super(GeneralLedger, self).__init__(cr, uid, name, context)
		self.localcontext.update( {
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
		#ctx['periods'] = form['periods'][0][2]
		query = self.pool.get('account.move.line')._query_get(self.cr, self.uid, context=ctx)
		
		sSQL = "SELECT l.date, j.code, m.name as jv_name, p.name as pname, a.name as aname, l.ref, l.name, l.debit, l.credit "\
			"FROM  account_journal j, account_account a, account_move m, account_move_line l "\
            "LEFT JOIN res_partner p " \
            "ON (l.partner_id = p.id) " \
			"WHERE l.journal_id = j.id AND l.account_id = a.id AND m.id = l.move_id "\
			"AND l.date >= '" + datas['date1'] + "'"\
            "AND l.date <= '" + datas['date2'] + "' " \
			"AND account_id = " + str(account.id) +  " AND " + query + " "\
			"ORDER by l.date,l.move_id,pname "
		self.cr.execute(sSQL)
		res = self.cr.dictfetchall()

		sum = 0.0
		for l in res:
			ans = l['debit'] - l ['credit']
			sum += ans
			ans = sum
			if ans > 0:
			    ans = str(ans) + " Dr."
			else:
			    ans = ans * -1
			    ans = str(ans) + " Cr."
			
			l['progress'] = ans
		return res

	def _sum_debit_account(self, account, form):
		ctx = self.context.copy()
		ctx['fiscalyear'] = form['fiscalyear']
		#ctx['periods'] = form['periods'][0][2]
		query = self.pool.get('account.move.line')._query_get(self.cr, self.uid, context=ctx)
		self.cr.execute("SELECT sum(debit) "\
				"FROM account_move_line l "\
				"WHERE l.account_id = %d " \
				"AND l.date >= '" + form['date1'] + "' "\
                "AND l.date <= '" + form['date2'] + "' " \
                "AND "+query, (account.id,))
		return self.cr.fetchone()[0] or 0.0

	def _sum_credit_account(self, account, form):
		ctx = self.context.copy()
		ctx['fiscalyear'] = form['fiscalyear']
		#ctx['periods'] = form['periods'][0][2]
		query = self.pool.get('account.move.line')._query_get(self.cr, self.uid, context=ctx)
		self.cr.execute("SELECT sum(credit) "\
				"FROM account_move_line l "\
				"WHERE l.account_id = %d "\
				"AND l.date >= '" + form['date1'] + "' "\
                "AND l.date <= '" + form['date2'] + "' " \
                "AND "+query, (account.id,))
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
				"WHERE l.account_id in ("+','.join(map(str, self.ids))+") " \
				"AND l.date >= '" + form['date1'] + "' "\
                "AND l.date <= '" + form['date2'] + "' " \
                "AND "+query )
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
				"WHERE l.account_id in ("+','.join(map(str, self.ids))+") "\
				"AND l.date >= '" + form['date1'] + "' "\
                "AND l.date <= '" + form['date2'] + "' AND " +query)
		return self.cr.fetchone()[0] or 0.0

report_sxw.report_sxw(
	'report.account.general.ledger.custom.print',
	'account.account', 
	'addons/account_india/report/general_ledger.rml', 
	parser=GeneralLedger, 
	header=False
)