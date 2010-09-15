##############################################################################
#
# Copyright (c) 2005-2006 TINY SPRL. (http://tiny.be) All Rights Reserved.
#
# $Id: make_invoice.py 1070 2005-07-29 12:41:24Z nicoe $
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
import pooler

from mx import *
from mx import DateTime

invoice_form = """<?xml version="1.0"?>
<form string="Create invoices">
	<separator colspan="4" string="Are you sur you want to activate this service ?" />
	<field name="note" colspan="4" nolabel="1" readonly="1"/>
</form>
"""

invoice_fields = {
	'note': {'type':'text','string':'Note'}
}

ack_form = """<?xml version="1.0"?>
<form string="Service Activated">
	<label string="Invoices created" />
</form>"""

ack_fields = {}

def _get_default(self, cr, uid, data, context):
	if not context:
		context = {}
	sub = pooler.get_pool(cr.dbname).get('odms.subs_bundle').browse(cr, uid, data['id'], context)
	context['pricelist'] = sub.subscription_id.pricelist_id.id
	sub = pooler.get_pool(cr.dbname).get('odms.subs_bundle').browse(cr, uid, data['id'], context)
	price = sub.bundle_id.product_id.lst_price
	if sub.bundle_id.price_type=='byusers':
		price2 = price * sub.subscription_id.max_users
	else:
		price2 = price
	if sub.subscription_id.deadline_date:
		month = (DateTime.strptime(sub.subscription_id.deadline_date,'%Y-%m-%d') - DateTime.now()).days / 31
	else:
		month = 1
	price2 = price2 * month

	if sub.subscription_id.state in ('active','suspended'):
		note = """You are about to order a new service for your On Demand subscription:
	Service: %s
	Price: %.2f EUR / month %s

As usual, this fixed price includes:
  - Software
  - Hosting
  - Maintenance
  - Support

As your subscription is valid up the %s, if you want to
activate this service, we will invoice you %.2f EUR. This is the
price of this service up to this date, for a total of %d users.

Please confirm you want to activate this service.

	""" % (sub.bundle_id.name, price, sub.bundle_id.price_type=='byusers' and '* user' or '', sub.subscription_id.deadline_date or '???', price2,  sub.subscription_id.max_users)
	else:
		price = 0.0
		note = """You are about to order a new service for your On Demand subscription:
	Service: %s
	Price: %.2f EUR / month %s

As usual, this fixed price includes:
  - Software
  - Hosting
  - Maintenance
  - Support

As you are in a free trial mode, this service will not be invoiced to you.

Please confirm you want to activate this service.
""" % (sub.bundle_id.name, price, sub.bundle_id.price_type=='byusers' and '* user' or '')
	return {'note':note, 'price':price2}

def _makeInvoices(self, cr, uid, data, context):
	obj =  pooler.get_pool(cr.dbname).get('odms.subs_bundle')
	sub = obj.browse(cr, uid, data['id'], context)
	obj.install_bundle(cr, uid, [data['id']], context)
	if  data['form']['price']:
		obj.invoice_bundle(cr, uid, [data['id']], data['form']['price'], context)
	return True

class active_bundle(wizard.interface):
	states = {
		'init' : {
			'actions' : [_get_default],
			'result' : {
				'type' : 'form',
				'arch' : invoice_form,
				'fields' : invoice_fields,
				'state' : [('end', 'Do Not Activate This Service'),('active', 'I Agree') ]
			}
		},
		'active' : {
			'actions' : [],
			'result' : {'type' : 'action',
				    'action' : _makeInvoices,
				    'state' : 'end'}
		},
	}
active_bundle('odms.bundle.active')
