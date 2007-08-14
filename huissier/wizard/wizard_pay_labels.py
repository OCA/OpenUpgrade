# -*- coding: iso-8859-1 -*-
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

import time

import wizard
import netsvc

pay_form = '''<?xml version="1.0"?>
<form title="Paid ?">
	<field name="first"/>
	<field name="last"/>
	<field name="quantity"/>
	<field name="price"/>
	<field name="value"/>
	<field name="account_id"/>
</form>'''

pay_fields = {
	'first': {'string':u'De', 'type':'integer', 'readonly':True},
	'last': {'string':u'a', 'type':'integer', 'readonly':True},
	'quantity': {'string':u'Quantité', 'type':'integer', 'readonly':True},
	'price': {'string':u'Prix unitaire', 'type':'float', 'readonly':True},
	'value': {'string':u'Montant a payer', 'type':'float', 'readonly':True},
	'account_id': {'string':u'Compte destination', 'type':'many2one', 'required':True, 'relation':'account.account', 'domain':[('type','=','cash')]},
}

def _get_value(self, uid, datas):
	print "_get_value"
	service = netsvc.LocalService("object_proxy")
	res = service.execute(uid, 'huissier.vignettes', 'read', datas['ids'], ['first', 'last', 'quantity', 'price', 'value'])
	if not len(res):
		return {}
	return res[0]
	
def _pay_labels(self, uid, datas):
	print "_pay_labels"
	service = netsvc.LocalService("object_proxy")
	pay_id = service.execute(uid, 'huissier.vignettes', 'pay', [datas['id']], datas['form']['account_id'])
	return {}

class wizard_pay_labels(wizard.interface):
	states = {
		'init': {
			'actions': [_get_value], 
			'result': {'type': 'form', 'arch':pay_form, 'fields':pay_fields, 'state':[('pay','Payer les vignettes'), ('end','Annuler')]}
		},
		'pay': {
			'actions': [_pay_labels],
			'result': {'type': 'state', 'state':'end'}
		}
	}
wizard_pay_labels('huissier.labels.pay')


