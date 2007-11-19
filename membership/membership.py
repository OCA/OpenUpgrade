'''Membership'''
##############################################################################
#
# Copyright (c) 2007 TINY SPRL. (http://tiny.be) All Rights Reserved.
#
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

from osv import fields, osv
import time

STATE = [
	('none', 'Non Member'),
	('waiting', 'Waiting Member'),
	('invoiced', 'Invoiced Member'),
	('canceled', 'Canceled Member'),
	('paid', 'Paid Member'),
	('associated', 'Associated Member'),
	('free', 'Free Member'),
]

STATE_PRIOR = {
		'none' : 0,
		'canceled' : 1,
		'waiting' : 2,
		'invoiced' : 3,
		'associated' : 4,
		'free' : 5,
		'paid' : 6
		}


class membership_line(osv.osv):
	'''Member line'''

	def _state(self, cr, uid, ids, name, args, context=None):
		'''Compute the state lines'''
		res = {}
		for line in self.browse(cr, uid, ids):
			cr.execute('''
			SELECT i.state FROM
			account_invoice i WHERE
			i.id = (
				SELECT l.invoice_id FROM
				account_invoice_line l WHERE
				l.id = (
					SELECT  ml.account_invoice_line FROM
					membership_membership_line ml WHERE
					ml.id = %d
					)
				)
			''' % line.id)
			fetched = cr.fetchone()
			if not fetched :
				res[line.id] = 'canceled'
				continue
			istate = fetched[0]
			state = 'none'
			if (istate == 'draft') | (istate == 'proforma'):
				state = 'waiting'
			elif istate == 'open':
				state = 'invoiced'
			elif istate == 'paid':
				state = 'paid'
			elif istate == 'cancel':
				state = 'canceled'
			res[line.id] = state
		return res

	_description = __doc__
	_name = 'membership.membership_line'
	_columns = {
			'partner': fields.many2one('res.partner', 'Partner'),
			'date_from': fields.date('From'),
			'date_to': fields.date('To'),
			'date_cancel' : fields.date('Cancel date'),
			'account_invoice_line': fields.many2one('account.invoice.line', 'Account Invoice line'),
			'state': fields.function(_state, method=True, string='State', type='selection', selection=STATE),
			}
	_rec_name = 'partner'
	_order = 'id desc'

membership_line()



class Partner(osv.osv):
	'''Partner'''

	def _membership_state(self, cr, uid, ids, name, args, context=None):
		'''Compute membership state of partners'''

		res = {}
		today = time.strftime('%Y-%m-%d')
		
		for partner in self.browse(cr, uid, ids):
			pstate = 'none'
			if partner.free_member:
				pstate= 'free'
			elif partner.associate_member and partner.associate_member.id:
				pstate = 'associated'
			if partner.member_lines:
				for line in partner.member_lines:
					if (line.date_from <= today) and (line.date_to >= today):
						lstate = line.state
						if STATE_PRIOR[lstate] > STATE_PRIOR[pstate]:
							pstate = lstate
			res[partner.id] = pstate

		return res

	def _membership_state_search(self, cr, uid, obj, name, args):
		'''Search on membership state'''
		if not len(args):
			return []
		today = time.strftime('%Y-%m-%d')
		clause = 'WHERE'
		ids2 = []

		for arg in args:

			if arg[1] == '=':
				if str(arg[2]) != 'none':
					cr.execute('SELECT p.id \
							FROM res_partner AS p, membership_membership_line AS l \
							WHERE l.partner = p.id \
							AND l.date_from <= %s \
							AND l.date_to >= %s ',
							(today, today))
				else:
					cr.execute('SELECT p.id \
						FROM res_partner AS p \
						WHERE p.id NOT IN ( \
							SELECT partner \
							FROM membership_membership_line )')
				res = cr.fetchall()
				if not res:
					return [('id', '=', '0')]
				ids = [x[0] for x in res]
				for partner in self.browse(cr, uid, ids):
					if partner.membership_state == str(arg[2]):
						ids2.append(partner.id)

			elif arg[1] == '!=':
				if str(arg[2]) == 'none':
					cr.execute('SELECT p.id \
							FROM res_partner AS p, membership_membership_line AS l \
							WHERE l.partner = p.id \
							AND l.date_from <= %s \
							AND l.date_to >= %s '
							(today, today))
				else:
					cr.execute('SELECT p.id \
						FROM res_partner AS p \
						WHERE p.id NOT IN ( \
							SELECT partner \
							FROM membership_membership_line )')
				res = cr.fetchall()
				if not res:
					return [('id', '=', '0')]
				ids = [x[0] for x in res]
				for partner in self.browse(cr, uid, ids):
					if partner.membership_state != str(arg[2]):
						ids2.append(partner.id)

			return [('id', 'in', ids2)]

	def _membership_start(self, cr, uid, ids, name, args, context=None):
		'''Return the start date of membership'''
		res = {}
		member_line_obj = self.pool.get('membership.membership_line')
		for partner_id in ids:
			line_id = member_line_obj.search(cr, uid, [('partner', '=', partner_id)],
					limit=1, order='date_from ASC')
			if line_id:
				res[partner_id] = member_line_obj.read(cr, uid, line_id[0],
						['date_from'])['date_from']
			else:
				res[partner_id] = False
		return res

	def _membership_start_search(self, cr, uid, obj, name, args):
		'''Search on membership start date'''
		if not len(args):
			return []
		where = ' AND '.join(['date_from '+x[1]+' \''+str(x[2])+'\''
			for x in args])
		cr.execute('SELECT partner, MINCancel flight(date_from) \
				FROM ( \
					SELECT partner, MIN(date_from) AS date_from \
					FROM membership_membership_line \
					GROUP BY partner \
				) AS foo \
				WHERE '+where+' \
				GROUP BY partner')
		res = cr.fetchall()
		if not res:
			return [('id', '=', '0')]
		return [('id', 'in', [x[0] for x in res])]

	def _membership_stop(self, cr, uid, ids, name, args, context=None):
		'''Return the stop date of membership'''
		res = {}
		member_line_obj = self.pool.get('membership.membership_line')
		for partner_id in ids:
			line_id = member_line_obj.search(cr, uid, [('partner', '=', partner_id)],
					limit=1, order='date_to ASC')
			if line_id:
				res[partner_id] = member_line_obj.read(cr, uid, line_id[0],
						['date_to'])['date_to']
			else:
				res[partner_id] = False
		return res

	def _membership_stop_search(self, cr, uid, obj, name, args):
		'''Search on membership stop date'''
		if not len(args):
			return []
		where = ' AND '.join(['date_to '+x[1]+' \''+str(x[2])+'\''
			for x in args])
		cr.execute('SELECT partner, MIN(date_to) \
				FROM ( \
					SELECT partner, MIN(date_to) AS date_to \
					FROM membership_membership_line \
					GROUP BY partner \
				) AS foo \
				WHERE '+where+' \
				GROUP BY partner')
		res = cr.fetchall()
		if not res:
			return [('id', '=', '0')]
		return [('id', 'in', [x[0] for x in res])]

	def _membership_cancel(self, cr, uid, ids, name, args, context=None):
		'''Return the cancel date of membership'''
		res = {}
		member_line_obj = self.pool.get('membership.membership_line')
		for partner_id in ids:
			line_id = member_line_obj.search(cr, uid, [('partner', '=', partner_id)],
					limit=1, order='date_to ASC')
			if line_id:
				res[partner_id] = member_line_obj.read(cr, uid, line_id[0],
						['date_to'])['date_to']
			else:
				res[partner_id] = False
		return res

	def _membership_cancel_search(self, cr, uid, obj, name, args):
		'''Search on membership cancel date'''
		if not len(args):
			return []
		where = ' AND '.join(['date_to '+x[1]+' \''+str(x[2])+'\''
			for x in args])
		cr.execute('SELECT partner, MIN(date_to) \
				FROM ( \
					SELECT partner, MIN(date_to) AS date_to \
					FROM membership_membership_line \
					GROUP BY partner \
				) AS foo \
				WHERE '+where+' \
				GROUP BY partner')
		res = cr.fetchall()
		if not res:
			return [('id', '=', '0')]
		return [('id', 'in', [x[0] for x in res])]



	_inherit = 'res.partner'
	_columns = {
		'member_lines': fields.one2many('membership.membership_line', 'partner',
			'Membership'),
		'membership_amount': fields.float('Membership amount', digites=(16, 2),
			help='The price negociated by the partner'),
		'membership_state': fields.function(_membership_state, method=True, String='Current membership state',
			type='selection', selection=STATE),
		'associate_member': fields.many2one('res.partner', 'Associate member'),
		'free_member': fields.boolean('Free member'),
		'membership_start': fields.function(_membership_start, method=True,
			string='Start membership date', type='date',
			fnct_search=_membership_start_search),
		'membership_stop': fields.function(_membership_stop, method=True,
			string='Stop membership date', type='date',
			fnct_search=_membership_stop_search),
		'membership_cancel': fields.function(_membership_cancel, method=True,
			string='Cancel membership date', type='date',
			fnct_search=_membership_cancel_search),
	}
	_defaults = {
		'free_member': lambda *a: False,
	}

Partner()


class Product(osv.osv):
	'''Product'''

	_inherit = 'product.product'
	_columns = {
			'membership': fields.boolean('Membership', help='Specify if this product is a membership product'),
			'membership_date_from': fields.date('Date from'),
			'membership_date_to': fields.date('Date to'),
			}

	_defaults = {
			'membership': lambda *args: False
			}
Product()

class Invoice(osv.osv):
	'''Invoice'''

	_inherit = 'account.invoice'

	def action_move(self, cr, uid, ids, context=None):
		'''Update the membership state while changing the state of invoicing'''
		if context is None:
			context = {}
		partner_obj = self.pool.get('res.partner')
		member_line_obj = self.pool.get('membership.membership_line')
		
		for invoice in self.browse(cr, uid, ids):
			
			partner = partner_obj.search(cr, uid,
					[('id', '=', invoice.partner_id.id)], context)
			mlines = member_line_obj.search(cr, uid,
					[('partner', '=', partner.id)], context)


			for line in mlines:
				if not state:
					state = 'none'
				else:
					state = partner.membership_state

				lstate = line.state
				if comparator[lstate] > comparator[state]:
					state = lstate

				partner_obj.write(cr, uid, partner.id, {
					'membership_state' : state
					})


	def action_move_create(self, cr, uid, ids, context=None):
		'''Create membership.membership_line if the product is for membership'''
		if context is None:
			context = {}
		member_line_obj = self.pool.get('membership.membership_line')
		partner_obj = self.pool.get('res.partner')
		for invoice in self.browse(cr, uid, ids):

			# fetch already existing member lines
			former_mlines = member_line_obj.search(cr,uid,
					[('account_invoice_line','in',
						[ l.id for l in invoice.invoice_line])], context)
			# empty them :
			if former_mlines:
				member_line_obj.write(cr,uid,former_mlines, {'account_invoice_line':False}, context)

			for line in invoice.invoice_line:
				if line.product_id and line.product_id.membership:
					date_from = line.product_id.membership_date_from
					if invoice.date_invoice > date_from:
						date_from = invoice.date_invoice
					member_line_obj.create(cr, uid, {
						'partner': invoice.partner_id.id,
						'date_from': date_from,
						'date_to': line.product_id.membership_date_to,
						'account_invoice_line': line.id,
						})
		return super(Invoice, self).action_move_create(cr, uid, ids, context)

	def action_cancel(self, cr, uid, ids, context=None):
		'''Create a cancel_date on the membership_line object'''
		
		if context is None:
			context = {}
		member_line_obj = self.pool.get('membership.membership_line')
		today = time.strftime('%Y-%m-%d')

		for invoice in self.browse(cr, uid, ids):
			mlines = member_line_obj.search(cr,uid,
					[('account_invoice_line','in',
						[ l.id for l in invoice.invoice_line])], context)
			member_line_obj.write(cr,uid,mlines, {'cancel_date':today}, context)

Invoice()

#class ReportPartnerMemberYear(osv.osv):
#	'''Membership by Years'''
#
#	_name = 'report.membership.year'
#	_description = __doc__
#	_auto = False
#	_rec_name = 'year'
#	_columns = {
#		'year': fields.char('Year', size='4', readonly=True, select=1),
#		'state': fields.selection(STATE, 'State', readonly=True, select=1),
#		'number': fields.integer('Number', readonly=True),
#		'amount': fields.float('Amount', digits=(16, 2), readonly=True),
#		'currency': fields.many2one('res.currency', 'Currency', readonly=True,
#			select=2),
#	}
#
#	def init(self, cr):
#		'''Create the view'''
#		cr.execute("""
#			CREATE OR REPLACE VIEW report_membership_year AS (
#				SELECT
#					MIN(id) AS id,
#					year,
#					state,
#					SUM(number) AS number,
#					SUM(amount) AS amount,
#					currency
#				FROM
#					(SELECT
#						MIN(l.id) AS id,
#						TO_CHAR(l.date_from, 'YYYY') AS year,
#						CASE WHEN ((sol.state = 'cancel') OR
#							(p.membership_cancel IS NOT NULL
#								AND TO_CHAR(p.membership_cancel, 'YYYY')
#									= TO_CHAR(l.date_from, 'YYYY')))
#							THEN 'canceled'
#							ELSE CASE WHEN sol.invoiced
#								THEN CASE WHEN so.invoiced
#									THEN 'paid'
#									ELSE 'invoiced'
#									END
#								ELSE 'waiting'
#								END
#							END AS state,
#						COUNT(l.id) AS number,
#						SUM(sol.price_unit * sol.product_uom_qty * (1 - sol.discount / 100)) AS amount,
#						ppl.currency_id AS currency
#					FROM membership_membership_line l
#						JOIN (sale_order_line sol
#							LEFT JOIN sale_order so
#								LEFT JOIN product_pricelist ppl
#									ON (ppl.id = so.pricelist_id)
#								ON (sol.order_id = so.id))
#							ON (l.sale_order_line = sol.id)
#						JOIN res_partner p
#							ON (l.partner = p.id)
#					GROUP BY TO_CHAR(l.date_from, 'YYYY'), sol.state,
#						sol.invoiced, so.invoiced, p.membership_cancel, ppl.currency_id
#				) AS foo
#				GROUP BY year, state, currency
#			)""")
#
#ReportPartnerMemberYear()
#
#
#class ReportPartnerMemberYearNew(osv.osv):
#	'''New Membership by Years'''
#
#	_name = 'report.membership.year_new'
#	_description = __doc__
#	_auto = False
#	_rec_name = 'year'
#	_columns = {
#		'year': fields.char('Year', size='4', readonly=True, select=1),
#		'number': fields.integer('Number', readonly=True),
#		'amount': fields.float('Amount', digits=(16, 2),
#			readonly=True),
#		'currency': fields.many2one('res.currency', 'Currency', readonly=True,
#			select=2),
#	}
#
#	def init(self, cr):
#		'''Create the view'''
#		cr.execute("""
#			CREATE OR REPLACE VIEW report_membership_year_new AS (
#				SELECT
#					MIN(id) AS id,
#					TO_CHAR(date_from, 'YYYY') as year,
#					COUNT(id) AS number,
#					SUM(amount) AS amount,
#					currency
#				FROM (
#					SELECT
#						MIN(l1.id) AS id,
#						SUM(sol.price_unit * sol.product_uom_qty * ( 1 - sol.discount / 100)) AS amount,
#						l1.date_from,
#						ppl.currency_id AS currency
#					FROM
#						(SELECT
#							partner AS id,
#							MIN(date_from) AS date_from
#						FROM membership_membership_line
#						GROUP BY partner
#					) AS l1
#						JOIN membership_membership_line l2
#							JOIN sale_order_line sol
#								LEFT JOIN sale_order so
#									LEFT JOIN product_pricelist ppl
#										ON (ppl.id = so.pricelist_id)
#									ON (sol.order_id = so.id)
#								ON (l2.sale_order_line = sol.id)
#							ON (l1.id = l2.partner AND l1.date_from = l2.date_from)
#					GROUP BY ppl.currency_id, l1.id, l1.date_from
#				) AS foo
#				GROUP BY currency, TO_CHAR(date_from, 'YYYY')
#			)""")
#
#ReportPartnerMemberYearNew()
