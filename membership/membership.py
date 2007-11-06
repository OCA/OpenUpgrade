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

class Product(osv.osv):
	'''Product'''

	_inherit = 'product.product'
	_columns = {
			'membership': fields.boolean('Membership', help='Specify if this product is a membership product'),
			'membership_date_from': fields.date('Date from'),
			'membership_date_to': fields.date('Date to'),
			}

	_defaults = {
			}
Product()

class Line:
	'''Member line'''

	def _state(self, cursor, uid, ids, name, args, context=None):
		'''Compute the state lines'''
		res = {}
		for line in self.browse(cursor, uid, ids):
			state = 'waiting'
			if line.sale_order_line.invoiced:
				state = 'invoiced'
			if line.sale_order_line.order_id.invoiced:
				state = 'paid'
			if line.sale_order_line.state == 'cancel':
				state = 'canceled'
			res[line.id] = state
		return res

	_description = __doc__
	_name = 'membership.line'
	_columns = {
			'partner': fields.many2one('res.partner', 'Partner'),
			'date_from': fields.date('From'),
			'date_to': fields.date('To'),
			'sale_order_line': fields.many2one('sale.order.line', 'Sale order line'),
			'state': fields.function(_state, method=True, string='State', type='selection', selection=STATE),
			}
	_rec_name = 'partner'
	_order = 'id desc'
