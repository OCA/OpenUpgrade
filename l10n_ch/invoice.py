# -*- encoding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2004-2007 TINY SPRL. (http://tiny.be) All Rights Reserved.
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
from osv import fields, osv
from tools import mod10r


class account_invoice(osv.osv):
	_inherit = "account.invoice"

	def _get_reference_type(self, cursor, user, context=None):
		res = super(account_invoice, self)._get_reference_type(cursor, user,
				context=context)
		res.append(('bvr', 'BVR'))
		return res

	_columns = {
		'reference_type': fields.selection(_get_reference_type, 'Reference Type',
			required=True),
	}

	def _check_bvr(self, cr, uid, ids):
		"""
		0100054150009>132000000000000000000000014+ 1300132412>
		"""
		invoices = self.browse(cr,uid,ids)
		for invoice in invoices:
			if invoice.reference_type == 'bvr' \
					and invoice.reference \
					and mod10r(invoice.reference[:-1]) \
					!= invoice.reference:
				return False
		return True

	_constraints = [
		(_check_bvr, 'Error : Invalid Bvr Number (wrong checksum).', ['reference'])
	]

account_invoice()
