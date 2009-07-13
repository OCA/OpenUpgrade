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
import pooler

take_fields = {
}
take_form = """<?xml version="1.0"?>
<form title="Confirm">
    <separator string="Create Invoice(s)" colspan="4"/>
    <newline/>
</form>
"""


def _invoice(self, cr, uid, data, context):
	order_obj = pooler.get_pool(cr.dbname).get('labo.analysis.request')
	newinv = []
	ids = order_obj.invoice_create(cr, uid, data['ids'],context)
	cr.commit()
	return {
		'domain': "[('id','in', ["+','.join(map(str,ids))+"])]",
		'name': 'Invoices',
		'view_type': 'form',
		'view_mode': 'tree,form',
		'res_model': 'account.invoice',
		'view_id': False,
		'context': "{'type':'in_refund'}",
		'type': 'ir.actions.act_window'
	}
	return {}



class wiz_invoice(wizard.interface):
	states = {
		'init': {
			'actions': [],
			'result': {'type': 'form', 'arch' : take_form,'fields' : take_fields, 'state':[ ('end','Cancel'),('invoice','Create Invoice')]}
		},
		'invoice' : {
			'actions' : [_invoice],
			'result' : {'type' : 'action',
				'action' : _invoice,
				'state' : 'end'}
		},
	}
wiz_invoice('labo.invoice');

