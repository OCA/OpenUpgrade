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
import wizard
from osv import osv
import pooler
from osv import fields
import time



ask_form="""<?xml version="1.0"?>
<form string="Populate Payment : ">
<field name="entries"/>
</form>
"""
ask_fields={
		'entries': {'string':'Entries', 'type':'many2many',
					'relation': 'account.move.line',},
		}


def search_entries(self, cr, uid, data, context):

	pool= pooler.get_pool(cr.dbname)
	move_line_obj = pool.get('account.move.line')
	payment = pool.get('payment.order').read(cr,uid,data['id'],['date','type'])
	account_ids = pool.get('account.account').search(cr,uid,[('type','=','payable')])

	# Search for move line to pay:
	clause = [('reconcile_id', '=', False), ('credit', '>',0),('account_id','in',account_ids)]
	mline_ids = move_line_obj.search(cr, uid, clause ,context)


	if not mline_ids:
		ask_fields['entries']['domain']= [('id','in',[])]
		return {}
	
	invoice_obj= pool.get('account.invoice')
	## Search for the corresponding invoices
	cr.execute('''select DISTINCT i.id,l.id
				  from account_invoice i
				  inner join account_move m on (i.move_id = m.id)
					   inner join account_move_line l on (m.id = l.move_id)
				  where l.id in (%s) ''' % ",".join(map(str,mline_ids)))


	inv2lines= {}
	line2bank= {}
	for inv_id, line_id in cr.fetchall():
		inv2lines[inv_id]= inv2lines.get(inv_id,[])+[line_id]
	invoices= invoice_obj.browse(cr,uid,inv2lines.keys(),context=context)
	if payment['type'] != 'manual':
		## Evaluate the suitables bank account codes
		bank_type= pool.get('payment.type').suitable_bank_types(cr,uid,payment['type'],context=context)
		## Search a suitable bank for each invoice partner
		for invoice in invoices:
			for b in invoice.partner_id.bank_ids:
				if b.state in bank_type:	 # The state field contain (the code of) the type of bank
					line2bank.update([(x,b.id) for x in inv2lines[invoice.id]])
					break
	else :
		for invoice in invoices:
			if invoice.partner_id.bank_ids:
				line2bank.update([(x,invoice.partner_id.bank_ids[0].id) for x in inv2lines[invoice.id]])

	data['line2bank']= line2bank
	ask_fields['entries']['domain']= [('id','in',line2bank.keys()),('amount_to_pay','>',0)]
	return {}

def create_payment(self, cr, uid, data, context):
	line2bank= data.get('line2bank')
	if not line2bank: return {}
	mline_ids= data['form']['entries'][0][2]
	pool= pooler.get_pool(cr.dbname)
	payment_line_obj = pool.get('payment.line')
	payment = pool.get('payment.order').read(cr,uid,data['id'],['type'])

	## Finally populate the current payment with new lines:
	for line in pool.get('account.move.line').browse(cr,uid,mline_ids,context=context):
		payment_line_obj.create(cr,uid,{
			'move_line': line.id,
			'amount':line.credit,
			'bank':line2bank.get(line.id),
			'payment_order': payment['id'],
			})

	return {}

class wizard_payment_order(wizard.interface):
	"""
	Create a payment object with lines corresponding to the account move line
	to pay according to the date and the type provided by the user.
	Hypothesis:
	- Small number of non-reconcilied move line , payment type	and bank account type,
	- Big number of partner and bank account.

	If a type is given, unsuitable account move lines are ignored.
	"""
	states = {'init' : {'actions':[search_entries],		
						'result': {'type':'form',
							 'arch':ask_form,
							 'fields':ask_fields,
							 'state':[('end','_Cancel'),('create','_Next')]}

							 },

			  'create': {'actions': [], 
						 'result': {'type':'action',
									'action':create_payment,
									'state':'end'}
				},				
	
		}
wizard_payment_order('make_payment')


