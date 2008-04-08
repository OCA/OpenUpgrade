##############################################################################
#
# Copyright (c) 2005-2006 TINY SPRL. (http://tiny.be) All Rights Reserved.
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


import pooler
import netsvc
import wizard
from osv import osv


def _get_journal(self, cr, uid, context):
	pool=pooler.get_pool(cr.dbname)
	obj=pool.get('account.journal')
	ids = obj.search(cr, uid, [('type','=','cash')])
	res = obj.read(cr, uid, ids, ['id', 'name'], context)
	res = [(r['id'], r['name']) for r in res]
	return res


payment_form = """<?xml version="1.0"?>
<form string="Add payment :">
<field name="amount"/>
<field name="journal"/>
</form>
"""

payment_fields = {
	'amount': {'string':'Amount', 'type':'float','required': True,},
	'journal':{'string':'Journal',
 				'type':'selection',
 				'selection': _get_journal,
 				'required': True,
			   },
	}

def _pre_init(self, cr, uid, data, context):

	pool = pooler.get_pool(cr.dbname)
	order = pool.get('pos.order').browse(cr,uid,data['id'],context)
	j_obj = pool.get('account.journal')

	ids = j_obj.search(cr, uid, [('type','=','cash')])
	journal = 0
	existing = []

	for payment in order.payments:
		existing.append(payment.journal_id.id)
	for i in ids:
		if i not in existing:
			journal = i
			break
	if not journal:
		journal = ids[0]


	return {'amount': order.amount_total - order.amount_paid,
			'journal': journal}

def _add_pay(self, cr, uid, data, context):
	pool = pooler.get_pool(cr.dbname)
	order_obj = pool.get('pos.order')
	order_obj.add_payment(cr,uid,data['id'],data['form']['amount'],
						  data['form']['journal'],context=context)

	return {}

def _check(self, cr, uid, data, context):
	"""Check the order:
	if the order is not paid: continue payment,
	if the order is paid print invoice or ticket.
	"""

	pool = pooler.get_pool(cr.dbname)
	order_obj = pool.get('pos.order')
	order = order_obj.browse(cr,uid,data['id'],context)
	#if not order.amount_total:
	#	return 'receipt'
	order_obj.test_order_lines(cr,uid,order,context=context)
	return (order.state == 'paid') and  \
		   (order.partner_id and 'invoice' or 'receipt') or \
		   'ask_pay'

def create_invoice(self, cr, uid, data, context):
	order = pooler.get_pool(cr.dbname).get('pos.order')

	wf_service = netsvc.LocalService("workflow")
	for i in data['ids']:
		wf_service.trg_validate(uid, 'pos.order', i, 'invoice', cr)

	return {}


class pos_payment(wizard.interface):

	states = {
		'init' : {'actions' : [],
				  'result' : {'type' : 'choice',
							  'next_state': _check,
							  }
				  },
		'ask_pay' : {'actions' : [_pre_init],
				 'result' : {'type' : 'form',
							 'arch': payment_form,
							 'fields': payment_fields,
							 'state' : (('end', 'Cancel'),
										('add_pay', 'Ma_ke payment',
										 'gtk-ok', True)
										)
							 }
				 },
		'add_pay' : {'actions' : [_add_pay],
					 'result' : {'type' : 'state',
								 'state': "init",
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
