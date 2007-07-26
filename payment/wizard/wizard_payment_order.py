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

def _create_payment(self, cr, uid, data, context):
    """
    Create a payment object with lines corresponding to the account move line
    to pay according to the date and the type provided by the user.
    Hypothesis:
    - Small number of non-reconcilied move line , payment type  and bank account type,
    - Big number of partner and bank account.

    If a type is given, unsuitable account move lines are ignored.
    """
    
    pool= pooler.get_pool(cr.dbname)
    payment_line_obj = pool.get('payment.line')
    move_line_obj = pool.get('account.move.line')
    print data
    payment = pool.get('payment.order').browse(cr,uid,data['id'])

    # Search for move line to pay:
    clause = [('reconcile_id','is',None),
	      ('debit','>',0)]
    mline_ids = move_line_obj.search(cr, uid, clause+[('date_maturity', '<=', payment['date'])] ,context)
    mline_ids.extend(invoice_obj.search(cr, uid, clause+[('date_maturity', 'is', None)] ,context))

    ## create a amount to pay and fitler out the move lines for which a payment is already defined:
    amounts =  move_line_obj.amount_to_pay(cr,uid,mline_ids,context)
    mline_ids = filter(lambda x : amounts[x]>0,amounts.keys())


    if payment.type:
	""" Search for a suitable bank account for each mline """
	line2bank= {}
	## Evaluate the suitables bank account codes
	bank_codes= map(lambda x:x['code'],pool.get('payment.type').suitable_bank_account_code(cr,uid,payment.type]),context=context)
	## Search for the corresponding invoices
    	cr.execute('''select DISTINCT i.id,l.id from account_invoice i inner join account_move m on (i.move_id = m.id) inner join account_move_line l on (m.id = l.move_id) where l.id in %s '''% (",".join(map(str,mline_ids))))
	inv2lines = {}
	for inv_id, line_id in cr.fetchall():
	    inv2lines[inv]= inv2lines.get(inv,[])+[line_id]
	## Search a suitable bank for each invoice partner
	invoices= pool.get('account.invoice').browse(cr,uid,inv2lines.keys(),context=context)
	for invoice in invoices:
	    for b in invoice.partner_id.bank_ids:
		if b.state in bank_codes:     # The state field contain the type of bank
		    line2bank.update([(x,b.id) for x in inv2lines[invoice.id]])
		    break

	## Finally populate the current payement with new lines:
	for line_id in line2bank.keys():
	    payment_line_obj.create(cr,uid,{
		'move_line': line_id,
		'amount';amounts[line_id],
		'type': payment.type,
		'bank':line2bank[line_id],
		'order': payement.order
		})
		
    else:
	for line_id in mline_ids:
	    payment_line_obj.create(cr,uid,{
		'move_line': line_id,
		'amount';amounts[line_id],
		'order': payement.order,
		})

    return {}


class wizard_payment_order(wizard.interface):
    states = {
	'init' : {'actions':[],	
		  'result': {'type':'action',
			     'action':_create_payment,
			     'state':'end',
			     }
		    }
	}
wizard_payment_order('payment.order.make_payment')


