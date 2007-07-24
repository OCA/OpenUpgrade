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
import math
from osv import osv
from tools.misc import UpdateableStr
import pooler
import netsvc
from osv import fields

import mx.DateTime
from mx.DateTime import RelativeDateTime, now, DateTime, localtime


payment_form = """<?xml version="1.0"?>
<form string="Generate Payment Order">
<separator string="Generate Payment Order such as :" colspan="4"/>
  <field name="type"/>
  <newline/>
  <field name="payment_date"/>
</form>"""

def type_get(self,cr,uid,context):
    pay_type_obj = pooler.get_pool(cr.dbname).get('payment.type')
    ids = pay_type_obj.search(cr, uid, [])
    res = pay_type_obj.read(cr, uid, ids, ['code','name'], context)
    return [(r['name'],r['name']) for r in res]

payment_fields = {
    'type' : {'string':'Payment Type is',
              'type':'selection',
              'selection':type_get,
              'default':lambda *a:'Manual',
              'required': True,
              'help':'Choose the prefered payment for the invoices, unrelevant invoices will be ignored. Choose Manual to pay all the invoices.'},
    'payment_date' : {'string':"Payment Date is",
                      'type':'date',
                      'help':'Leave blank to pay the invoices without due date.'}
}

def _create_payment(self, cr, uid, data, context):
    """
    Create a payment object with lines corresponding to the invoices
    to pay according to the date and the type provided by the user.
    Hypothesis:
    - Small number of opened invoices, payment type  and bank account type,
    - Big number of partner and bank account.
    """
    
    form = data['form']
    pool= pooler.get_pool(cr.dbname)
    invoice_obj = pool.get('account.invoice')
    payment_line_obj = pool.get('payment.line')
    payment_term_obj=pool.get('account.payment.term')

    clause = [('state','=','open')]
    if form['payment_date']:
        inv_ids = invoice_obj.search(cr, uid, clause+[('date_due', '<=', form['payment_date'])] ,context)
    else:
        inv_ids = invoice_obj.search(cr, uid, clause+[('date_due', 'is', None)] ,context)

    ## create a list of payment to do:
    amount_to_pay =  invoice_obj.amount_to_pay(cr,uid,inv_ids,context)
    ## Evaluate the compatibles bank account types:
    bank_acc_types= map(lambda x:x['name'],pool.get('payment.type').compatible_bank_account_type(cr,uid,form['type']))
    
    pay_lines= []
    for invoice in invoice_obj.browse(cr, uid, map(lambda x:x[0],amount_to_pay), context):
	if amount_to_pay[invoice.id] <= 0: continue
        bank= False
	## Search for compatible bank
        for b in invoice.partner_id.bank_ids:
            if b.state in bank_acc_types:     # The state field contain the type of bank
                bank= True
                break
        if not bank :
	    continue

	# TODO : manage payment terms !

	
        pay_lines.append({'invoice_id':invoice.id, 'amount': amount_to_pay[invoice.id]})

    if pay_lines:
        payment_id= pool.get('payment.order').create(cr,uid,{
            'date': form['payment_date'],
            'type': form['type'],
            'payment_lines': [(0,0,pay_lines)]
            })
	return {        
	    'domain': "[('id','in', [%d])]"%payment_id,
	    'name': 'Payment orders',
	    'view_mode': 'form,tree',
	    'view_type':'form',
	    'res_model': 'payment.order',
	    'view_id': False,
	    'type': 'ir.actions.act_window'
	}

    return {        
	'name': 'Payment orders',
	'view_mode': 'form,tree',
	'view_type':'form',
	'res_model': 'payment.order',
	'view_id': False,
	'type': 'ir.actions.act_window'
    }

#     if res:
#         for invoice in res:
#             if(invoice.amount_to_pay > 0):
#                 amount_to_pay=amount=invoice.amount_to_pay
#                 amount_pay=invoice.amount_pay
#                 # sum of all due amount with given date
#                 if(invoice.payment_term):
#                         res_term=invoice.payment_term.compute(cr,uid,invoice.payment_term.id,invoice.amount_to_pay ,invoice.date_invoice)
#                         amount=0
#                         for res_date,res_amount in res_term:
#                             print invoice.id, res_date,res_amount
#                             if mx.DateTime.strptime(res_date, '%Y-%m-%d') < invoice.date_invoice :
#                                 amount +=res_amount


#                 pay_line = {
#                        'invoice_id':invoice.id,
#                        'amount':amount,
#                         }
#                 pay_lines.append(pay_line)




#     if (pay_lines):
#         state='draft'
#         if form['type']=='manual':
#             state='done'
#         pay_order = {
#            'name':form['payment_date'],
#            'state':state,
#            'type':form['type'],

#           }
#         pay_id=pay_obj.create(cr,uid,pay_order)
#         for pay_line in pay_lines:
#              pay_line['order_id']=pay_id
#              pay_order_line.create(cr,uid,pay_line)


    return {}



#FIXME: this doesn't do anything...

class wizard_payment_order(wizard.interface):
    states = {
        'init' : {
            'actions' : [],
            'result' : {'type':'form', 'arch':payment_form, 'fields':payment_fields, 'state':[('end', '_Cancel'),('payment','Create Payment _Order')]}

                },

	'payment':{'actions':[],
		  'result': {'type':'action',
			     'action':_create_payment,
			     'state':'end',
			     }
		    }
	}
wizard_payment_order('payment.order.make_payment')

#  LocalWords:  assomption
