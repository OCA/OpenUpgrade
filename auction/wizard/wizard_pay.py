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
	<field name="buyer_id"/>
	<newline/>
	<field name="amount"/>
	<field name="statement_id" />
	<field name="amount2"/>
	<field name="statement_id2" />
	<field name="amount3"/>
	<field name="statement_id3" />
</form>'''

def _start(self,cr,uid,data,context):
	pool = pooler.get_pool(cr.dbname)
	rec=pool.get('auction.lots').browse(cr,uid,data['id'],context)
	amount1= rec and rec.buyer_price or False
	return {'amount':amount1}


def _get_period(cr, uid, context):
	periods = self.pool.get('account.period').find(cr, uid)
	if periods:
		return periods[0]
	else:
		return False

pay_fields = {
	'amount': {'string': 'Amount paid', 'type':'float', 'required':True},
	'buyer_id': {'string': 'Buyer', 'type': 'many2one', 'relation':'res.partner', 'required':True},
	'statement_id': {'string':'Statement', 'type':'many2one', 'required':True, 'relation':'account.bank.statement.line'},
	'amount2': {'string': 'Amount paid', 'type':'float'},
	'statement_id2': {'string':'Statement', 'type':'many2one', 'relation':'account.bank.statement.line'},
	'amount3': {'string': 'Amount paid', 'type':'float'},
	'statement_id3': {'string':'Statement', 'type':'many2one', 'relation':'account.bank.statement.line'},
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
	for lot in lots:
		new_statement=pooler.get_pool(cr.dbname).get('account.bank.statement').create(cr,uid,{'journal_id':lot.auction_id.journal_id.id,
																							'balance_start':0,
																							'balance_end_real':0, 
																							'state':'draft',})
		new_id=pooler.get_pool(cr.dbname).get('account.bank.statement.line').write(cr,uid,[data['form']['statement_id']],{
																							'date': time.strftime('%Y-%m-%d'),
																							'partner_id':lot.ach_uid.id,
																							'type':'customer',
																							'statement_id':new_statement,
																							'account_id':lot.auction_id.acc_income.id,
																							'amount':-data['form']['amount']
																							})
	
	#	up_payment=pooler.get_pool(cr.dbname).get('auction.lots').write(cr,uid,[lot.id],{'statement_id': new_id})
	#	up_statement=pooler.get_pool(cr.dbname).get('account.bank.statement').write(cr,uid,[new_statement],{'line_ids': [(6,0,[new_id])]})
		if (data['form']['amount2']>0) and (data['form']['statement_id2']):
			new_id2=pooler.get_pool(cr.dbname).get('account.bank.statement.line').write(cr,uid,[data['form']['statement_id2']],{
																							'date': time.strftime('%Y-%m-%d'),
																							'partner_id':lot.ach_uid.id,
																							'type':'customer',
																							'statement_id':new_statement,
																							'account_id':lot.auction_id.acc_income.id,
																							'amount':-data['form']['amount2']
																							})
		if (data['form']['amount3']>0) and (data['form']['statement_id3']):
			new_id3=pooler.get_pool(cr.dbname).get('account.bank.statement.line').write(cr,uid,[data['form']['statement_id3']],{
																							'date': time.strftime('%Y-%m-%d'),
																							'partner_id':lot.ach_uid.id,
																							'type':'customer',
																							'statement_id':new_statement,
																							'account_id':lot.auction_id.acc_income.id,
																							'amount':-data['form']['amount3']
																							})
#	if data['form']['amount1'] and data['form']['amount2'] and data['form']['amount3']:
#		pool.get('account.bank.statement').write(cr,uid,[new_statement],{'balance_end_real': -data['form']['amount1']-data['form']['amount2']-data['form']['amount3']})
#	elif data['form']['amount1'] and data['form']['amount2']:
#		pool.get('account.bank.statement').write(cr,uid,[new_statement],{'balance_end_real': -data['form']['amount1']-data['form']['amount2']})
#	elif data['form']['amount1'] :
#		pool.get('account.bank.statement').write(cr,uid,[new_statement],{'balance_end_real': -data['form']['amount1']})
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
			'actions': [_start],
			'result': {'type': 'form', 'arch':pay_form, 'fields': pay_fields, 'state':[('end','Cancel'),('pay','Pay')]}
		},
		'pay': {
		'actions': [_pay_and_reconcile],
		'result': {'type': 'state', 'state':'end'}
		}}
wiz_auc_lots_pay('auction.pay.buy')


