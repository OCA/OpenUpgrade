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
import pooler
import wizard
import netsvc

reprint_form = '''<?xml version="1.0"?>
<form title="Paiement du lot">
	<field name="scan_code" colspan="4"/>
</form>'''

reprint_fields = {
#	'scan_code': {'string':u'Code client', 'type':'char', 'required':True},
	'scan_code': {'string': 'client', 'type': 'many2one', 'relation':'res.partner'},

}

#def _get_value(self, uid, datas):
#	return {}
def def_payment(self, cr, uid, data, context):
	pool = pooler.get_pool(cr.dbname)
	code_client=data['form']['scan_code'] 
	find_id= pool.get('res.partner').browse(cr,uid,data['form']['scan_code'])
	pool.get('huissier.lots').write(cr,uid,data['ids'],{'state':'vendu','buyer_ref':find_id.id})
	return {}


class wizard_payment(wizard.interface):
	states = {
		'init': {
			'actions': [], 
			'result': {'type':'form', 'arch':reprint_form, 'fields':reprint_fields, 'state':[('payer','payer'), ('end','Annuler')]}
		},
		'payer': {
			'actions': [def_payment],
			'result': {'type':'state', 'state':'end'}
		}
	}
wizard_payment('huissier.lots.payment')


