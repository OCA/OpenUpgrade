##############################################################################
#
# Copyright (c) 2005-2006 TINY SPRL. (http://tiny.be) All Rights Reserved.
#
# $Id: wizard_partial_picking.py 4304 2006-10-25 09:54:51Z ged $
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


import netsvc
import pooler

import wizard
from osv import osv


def pay_n_check(self, cr, uid, data, context):
	pool = pooler.get_pool(cr.dbname)
	order = pool.get('pos.order').browse(cr,uid,data['id'],context)
	try:
		if order.payment_ids:
			order.button_ok_complex(cr, uid, data['ids'], context)
		else:
			order.button_ok_simple(cr, uid, data['ids'], context)
			pool.get('pos.payment').create(cr,uid,{
				'order_id': order.id,
				'journal_id': order.journal_id,
				'amount': order.amount_total
				})


 	except osv.except_osv, e:
		raise wizard.except_wizard(e.name, e.value)


	return order.partner_id and 'invoice' or 'receipt'


def create_invoice(self, cr, uid, data, context):
	order = pooler.get_pool(cr.dbname).get('pos.order')
	try:
		inv_ids = order.create_invoice(cr, uid, data['ids'], context)
	except osv.except_osv, e:
		raise wizard.except_wizard(e.name, e.value)
	
	return {}


class pos_payment(wizard.interface):

	states = {
		'init' : {
			'actions' : [],
			'result' : {'type' : 'choice',
						'next_state': pay_n_check
						}
		},

		'invoice' : {
			'actions' : [create_invoice],
			'result' : {'type' : 'print',
						'report': 'pos.invoice',
						'state':'end'
						}
		},
		'receipt' : {
			'actions' : [],
			'result' : {'type' : 'print',
						'report': 'pos.receipt',
						'state' : 'end'
						}
		},
		
	}
	

pos_payment('pos.payment')
