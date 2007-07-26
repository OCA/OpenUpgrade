##############################################################################
#
# Copyright (c) 2004 TINY SPRL. (http://tiny.be) All Rights Reserved.
#                    Fabien Pinckaers <fp@tiny.Be>
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
import netsvc
import netsvc
import osv
import time
import pooler
#field name="dest_account_id"/>
#	<field name="period_id"/>

#'period_id': {'string': 'Period', 'type': 'many2one', 'relation':'account.period'},
#'dest_account_id': {'string':'Payment to Account', 'type':'many2one', 'required':True, 'relation':'account.account', 'domain':[('type','=','cash')]},
pay_form = '''<?xml version="1.0"?>
<form string="Pay invoice">
	<field name="amount"/>
	<field name="dest_account_id"/>
	<field name="journal_id" domain="[('type','=','cash')]"/>
</form>'''


def _get_period(cr, uid, context):
	periods = self.pool.get('account.period').find(cr, uid)
	if periods:
		return periods[0]
	else:
		return False

pay_fields = {
	'amount': {'string': 'Amount paid', 'type':'float', 'required':True},
	'journal_id': {'string': 'Journal', 'type': 'many2one', 'relation':'account.journal', 'required':True},
	'dest_account_id': {'string':'Payment to Account', 'type':'many2one', 'required':True, 'relation':'account.account', 'domain':[('type','=','cash')]},
}
#def pay_n_check(self, cr, uid, data, context):
#
#	auction = pool.get('auction.lots').browse(cr,uid,data['id'],context)
#	try:
#		
#		for lot in auction:
#                            
#        	if not lot.auction_id :
#            	raise osv.except_osv("Error","No payment defined for this auction.")
#			i=1
#			tot= 0
#			for payment in auction:
#				if not payment.journal_id :
#					raise osv.except_osv("Error","No journal defined for the payment line %d" % (i,))
#				if not payment.ach_inv_id.amount :
#					raise osv.except_osv("Error","No amount defined for the payment line %d." % (i,))
#				i+=1
#				tot+= payment.ach_inv_id.amount
#			if abs(float(tot)) - abs(float(lot.obj_ret)) > 10**-6:
#				raise osv.except_osv("Error","The amount paid does not match the total amount")
#		else:
#			for lot in auction:
#              if not lot.journal_id :
#				raise osv.except_osv("Error","Please choose a journal for the auction ("+lot.name+").")
#			pool.get('auction.lots').create(cr,uid,{
#				'auction_id': lot.auction.id,
#				'journal_id': lot.journal_id,
#
#				})
# 	except osv.except_osv, e:
#		raise wizard.except_wizard(e.name, e.name)
#	return True


def _pay_and_reconcile(self, cr, uid, data, context):
	pool = pooler.get_pool(cr.dbname)
	lots = pool.get('auction.lots').browse(cr,uid,data['ids'],context)
	form = data['form']
	journal = form['journal_id']
	for lot in lots:
		new_id=pooler.get_pool(cr.dbname).get('account.bank.statement.line').create(cr,uid,{'name':lot.product_id.id,
																							'partner_id':lot.ach_uid.id,
																							'account_id':form['dest_account_id'],
																							'amount':form['amount']
																							})
		
		up_payment=pooler.get_pool(cr.dbname).get('account.bank.statement').write(cr,uid,[lot.statement.id],{'journal_id':journal,
																								'line_ids': [(6,0,[new_id])]
																								})
	return {}



	#	pool = pooler.get_pool(cr.dbname)
#	lot = pool.get('auction.lots').browse(cr,uid,data['id'],context)
#	form = data['form']
#	account_id = form.get('writeoff_acc_id', False)
#	period_id = form.get('period_id', False)
#	if not period_id:
#		periods = pool.get('account.period').find(cr, uid)
#		if periods:
#			period_id = periods[0]
#
#	journal_id = form.get('journal_id', False)
#	if lot.ach_inv_id:
#		#p=pool.get('account.invoice').pay_and_reconcile(['lot.ach_inv_id.id'], form['amount'], form['dest_account_id'], journal_id, account_id, period_id, journal_id, context)
#	return {}


class wiz_auc_lots_pay(wizard.interface):
	states = {
		'init': {
			'actions': [],
			'result': {'type': 'form', 'arch':pay_form, 'fields': pay_fields, 'state':[('pay','Pay'), ('end','Cancel')]}
		},
			'pay': {
			'actions': [_pay_and_reconcile],
			'result': {'type': 'state', 'state':'end'}
		}}
wiz_auc_lots_pay('auction.pay.buy');


