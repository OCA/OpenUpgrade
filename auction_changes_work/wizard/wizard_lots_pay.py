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

invoice_form = '''<?xml version="1.0"?>
<form title="Paid ?">
	<field name="amount"/>
	<field name="objects"/>
	<field name="amount_topay"/>
	<field name="amount_paid"/>
	<newline/>
	<field name="ach_uid" colspan="3"/>
	<field name="number" colspan="3"/>
</form>'''

invoice_fields = {
	'amount': {'string':'Invoiced Amount', 'type':'float', 'required':True, 'readonly':True},
	'amount_topay': {'string':'Amount to pay', 'type':'float', 'required':True, 'readonly':True},
	'amount_paid': {'string':'Amount paid', 'type':'float', 'readonly':True},
	'objects': {'string':'# of objects', 'type':'integer', 'required':True, 'readonly':True},
	'ach_uid': {'string':'Buyer Name', 'type':'many2one', 'required':True, 'relation':'res.partner'},
	'number': {'string':'Invoice Number', 'type':'integer'},
}

pay_form = '''<?xml version="1.0"?>
<form title="Paid ?">
	<field name="amount"/>
	<field name="objects"/>
	<newline/>
	<field name="ach_uid" colspan="3"/>
	<field name="account_id" colspan="3"/>
</form>'''

pay_fields = {
	'amount': {'string':'Amount to pay', 'type':'float', 'required':True, 'readonly':True},
	'objects': {'string':'# of objects', 'type':'integer', 'required':True, 'readonly':True},
	'ach_uid': {'string':'Buyer Name', 'type':'many2one', 'relation':'res.partner'},
	'account_id': {'string':'Payment to Account', 'type':'many2one', 'required':True, 'relation':'account.account', 'domain':[('type','=','cash')]},
}

def _get_value(self, uid, datas):
	service = netsvc.LocalService("object_proxy")
	lots = service.execute(uid, 'auction.lots', 'read', datas['ids'])
	auction = service.execute(uid, 'auction.dates', 'read', [lots[0]['auction_id'][0]])[0]
	ids = []
	price = 0.0
	uid = False
	for lot in lots:
		if not lot['ach_pay_id']:
			ids.append(lot['id'])
			
			price += lot['obj_price'] or 0.0
			
			costs = service.execute(uid, 'auction.lots', 'compute_buyer_costs', [lot['id']])
			for cost in costs:
				price += cost['amount']

			if lot['ach_uid']:
				if uid and (lot['ach_uid'][0]<>uid):
					raise wizard.except_wizard('UserError', ('Two different buyers for the same payment !\nPlease correct this problem before paying', 'init'))
				uid = lot['ach_uid'][0]
			elif lot['ach_login']:
				refs = service.execute(uid, 'res.partner', 'search', [('ref','=',lot['ach_login'])])
				if len(refs):
					uid = refs[-1]
	if len(ids)<len(datas['ids']):
		raise wizard.except_wizard('UserError', ('%d object(s) are already paid !' % (len(datas['ids'])-len(ids),), 'init'))
	return {'objects':len(ids), 'amount':price, 'ach_uid':uid}

def _pay(self, uid, datas):
	service = netsvc.LocalService("object_proxy")
	lots = service.execute(uid, 'auction.lots', 'lots_pay', datas['ids'],  datas['form']['ach_uid'], datas['form']['account_id'], datas['form']['amount'])
	return {}

def _get_value_invoice(self, uid, datas):
	service = netsvc.LocalService("object_proxy")
	lots = service.execute(uid, 'auction.lots', 'read', datas['ids'])
	auction = service.execute(uid, 'auction.dates', 'read', [lots[0]['auction_id'][0]])[0]
	
	price = 0.0
	price_topay = 0.0
	price_paid = 0.0
	uid = False
	for lot in lots:
		price_lot = lot['obj_price'] or 0.0
		
		costs = service.execute(uid, 'auction.lots', 'compute_buyer_costs', [lot['id']])
		for cost in costs:
			price_lot += cost['amount']
			
		price += price_lot
		
		if lot['ach_uid']:
			if uid and (lot['ach_uid'][0]<>uid):
				raise wizard.except_wizard('UserError', ('Two different buyers for the same invoice !\nPlease correct this problem before invoicing', 'init'))
			uid = lot['ach_uid'][0]
		elif lot['ach_login']:
			refs = service.execute(uid, 'res.partner', 'search', [('ref','=',lot['ach_login'])])
			if len(refs):
				uid = refs[-1]
		if lot['ach_pay_id']:
			price_paid += price_lot
		else:
			price_topay += price_lot

#TODO: recuperer id next invoice (de la sequence)???
	invoice_number = False
	return {'objects':len(datas['ids']), 'amount':price, 'ach_uid':uid, 'amount_topay':price_topay, 'amount_paid':price_paid, 'number':invoice_number}

def _invoice(self, uid, datas):
	service = netsvc.LocalService("object_proxy")
	service.execute(uid, 'auction.lots', 'lots_invoice_and_cancel_old_invoice', datas['ids'], datas['form']['number'], datas['form']['ach_uid'], 'invoice_open')
	return {}

class wiz_auc_lots_pay(wizard.interface):
	states = {
		'init': {
			'actions': [_get_value],
			'result': {'type': 'form', 'arch':pay_form, 'fields': pay_fields, 'state':[('pay_and_invoice','Pay and Invoice'), ('pay_and_print','Pay and Print'), ('pay','Pay'), ('end','Cancel')]}
		},
		'pay_and_invoice': {
			'actions': [_pay, _get_value_invoice],
			'result': {'type': 'form', 'arch':invoice_form, 'fields': invoice_fields, 'state':[('invoice','Invoice'), ('end','Cancel')]}
		},
		'pay_and_print': {
			'actions': [_pay],
			'result': {'type': 'print', 'report':'report.auction.ach_bordereau', 'state':'end'}
		},
		'pay': {
			'actions': [_pay],
			'result': {'type': 'state', 'state':'end'}
		},
		'invoice': {
			'actions': [_invoice],
			'result': {'type': 'print', 'report':'auction.invoice', 'state':'end'}
		}
	}
wiz_auc_lots_pay('auction.lots.pay');


