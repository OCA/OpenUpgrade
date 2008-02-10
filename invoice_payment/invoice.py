# -*- encoding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2004-2006 TINY SPRL. (http://tiny.be) All Rights Reserved.
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

class account_invoice(osv.osv):
	_inherit = "account.invoice"
	def _compute_lines(self, cr, uid, ids, name, args, context={}):
		result = {}
		print 'ICI 0'
		for invoice in self.browse(cr, uid, ids, context):
			moves = self.move_line_id_payment_get(cr, uid, [invoice.id])
			src = []
			print 'ICI 1'
			lines = []
			for m in self.pool.get('account.move.line').browse(cr, uid, moves, context):
				print 'ICI 2'
				if m.reconcile_id:
					lines += map(lambda x: x.id, m.reconcile_id.line_id)
				elif m.reconcile_partial_id:
					lines += map(lambda x: x.id, m.reconcile_partial_id.line_partial_ids)
				src.append(m.id)
				print 'ICI 3'
			lines = filter(lambda x: x not in src, lines)
			result[invoice.id] = lines
		return result

	_columns = {
		'payment_ids': fields.function(_compute_lines, method=True, relation='account.move.line', type="many2many", string='Payments'),
	}
account_invoice()
