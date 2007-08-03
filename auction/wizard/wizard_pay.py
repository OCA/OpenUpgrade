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
pay_form = '''<?xml version="1.0"?>
<form string="Pay objects">
	<field name="amount"/>
	<field name="statement_id1" />
	<field name="amount2"/>
	<field name="statement_id2" />
	<field name="amount3"/>
	<field name="statement_id3" />
	<newline/>
	<field name="buyer_id"/>
	<field name="total"/>
</form>'''

def _start(self,cr,uid,data,context):
	pool = pooler.get_pool(cr.dbname)
	rec=pool.get('auction.lots').browse(cr,uid,data['ids'],context)
	amount1=0.0
	for r in rec:
		amount1+=r.buyer_price
		buyer= r and r.ach_uid.id or False
	return {'amount':amount1, 'total':amount1,'buyer_id':buyer}

pay_fields = {
	'amount': {'string': 'Amount paid', 'type':'float'},
	'buyer_id': {'string': 'Buyer', 'type': 'many2one', 'relation':'res.partner'},
	'statement_id1': {'string':'Statement', 'type':'many2one', 'required':True, 'relation':'account.bank.statement'},
	'amount2': {'string': 'Amount paid', 'type':'float'},
	'statement_id2': {'string':'Statement', 'type':'many2one', 'relation':'account.bank.statement'},
	'amount3': {'string': 'Amount paid', 'type':'float'},
	'statement_id3': {'string':'Statement', 'type':'many2one', 'relation':'account.bank.statement'},
	'total': {'string': 'Amount to paid', 'type':'float','readonly':True}
}

def _pay_and_reconcile(self, cr, uid, data, context):
	pool = pooler.get_pool(cr.dbname)
	rest=0.0
	lots = pool.get('auction.lots').browse(cr,uid,data['ids'],context)
	ref_bk_s=pooler.get_pool(cr.dbname).get('account.bank.statement.line')
	for lot in lots:
		if not data['form']['buyer_id']:
			raise wizard.except_wizard('Error !', 'No buyer for "%s": Please set one.'%(lot.name))
		else:
			pool.get('auction.lots').write(cr,uid,[lot.id],{'ach_uid':data['form']['buyer_id']})
		if not lot.auction_id:
			raise wizard.except_wizard('Error !', 'No auction date for "%s": Please set one.'%(lot.name))
		new_id=ref_bk_s.create(cr,uid,{'name':'Payment1:'+ lot.name,
										'date': time.strftime('%Y-%m-%d'),
										'partner_id':lot.ach_uid.id,
										'type':'customer',
										'statement_id':data['form']['statement_id1'],
										'account_id':lot.auction_id.acc_income.id,
										'amount':-data['form']['amount']
										})
		new_id2=ref_bk_s.create(cr,uid,{'name':'Payment2:'+ lot.name ,
										'date': time.strftime('%Y-%m-%d'),
										'partner_id':lot.ach_uid.id,
										'type':'customer',
										'statement_id':data['form']['statement_id2'],
										'account_id':lot.auction_id.acc_income.id,
										'amount':-data['form']['amount2']
										})
		new_id3=ref_bk_s.create(cr,uid,{'name':'Payment3:'+ lot.name ,
										'date': time.strftime('%Y-%m-%d'),
										'partner_id':lot.ach_uid.id,
										'type':'customer',
										'statement_id':data['form']['statement_id3'],
										'account_id':lot.auction_id.acc_income.id,
										'amount':-data['form']['amount3']
										})
		rest=data['form']['total']-(data['form']['amount']+data['form']['amount2']+data['form']['amount3'])
		if (data['form']['amount']>0) and (data['form']['statement_id1']):
			pool.get('auction.lots').write(cr,uid,[lot.id],{'statement_id':[(6,0,[new_id])]})
		if (data['form']['amount2']>0) and (data['form']['statement_id2']):
			pool.get('auction.lots').write(cr,uid,[lot.id],{'statement_id':[(4,new_id2)]})
		if (data['form']['amount3']>0) and (data['form']['statement_id3']):
			pool.get('auction.lots').write(cr,uid,[lot.id],{'statement_id':[(4,new_id3)]})
		if data['form']['total']==(data['form']['amount']+data['form']['amount2']+data['form']['amount3']):
			pool.get('auction.lots').write(cr,uid,[lot.id],{'is_ok':True})
		else:
			raise wizard.except_wizard('Error !', 'You should pay all the total: "%f" are missing to accomplish the payment.' %(round(rest,2)))
	return {}


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


