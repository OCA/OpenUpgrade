##############################################################################
#
# Copyright (c) 2004-2007 TINY SPRL. (http://tiny.be) All Rights Reserved.
#
# $Id: account.py 1005 2005-07-25 08:41:42Z nicoe $
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
import time

#
# Create an invoice based on selected timesheet lines
#

#
# TODO: check unit of measure !!!
#
class invoice_create(wizard.interface):
	def _get_accounts(self, cr, uid, data, context):
		if not len(data['ids']):
			return {}
		cr.execute("SELECT distinct(account_id) from account_analytic_line where id IN (%s)"% (','.join(map(str,data['ids'])),))
		account_ids = cr.fetchall()
		return {'accounts': [x[0] for x in account_ids]}

	def _do_create(self, cr, uid, data, context):
		pool = pooler.get_pool(cr.dbname)
		analytic_account_obj = pool.get('account.analytic.account')
		res_partner_obj = pool.get('res.partner')
		account_payment_term_obj = pool.get('account.payment.term')

		account_ids = data['form']['accounts'][0][2]
		invoices = []
		for account in analytic_account_obj.browse(cr, uid, account_ids, context):
			partner = account.partner_id
			if (not partner) or not (account.pricelist_id):
				raise wizard.except_wizard('Analytic account incomplete',
						'Please fill in the partner and pricelist field '
						'in the analytic account:\n%s' % (account.name,))

			date_due = False
			if partner.property_payment_term:
				pterm_list= account_payment_term_obj.compute(cr, uid,
						partner.property_payment_term.id, value=1,
						date_ref=time.strftime('%Y-%m-%d'))
				if pterm_list:
					pterm_list = [line[0] for line in pterm_list]
					pterm_list.sort()
					date_due = pterm_list[-1]

			curr_invoice = {
				'name': time.strftime('%D')+' - '+account.name,
				'partner_id': account.partner_id.id,
				'address_contact_id': res_partner_obj.address_get(cr, uid,
					[account.partner_id.id], adr_pref=['contact'])['contact'],
				'address_invoice_id': res_partner_obj.address_get(cr, uid,
					[account.partner_id.id], adr_pref=['invoice'])['invoice'],
				'payment_term': partner.property_payment_term.id or False,
				'account_id': partner.property_account_receivable.id,
				'currency_id': account.pricelist_id.currency_id.id,
				'date_due': date_due,
			}
			last_invoice = pool.get('account.invoice').create(cr, uid, curr_invoice)
			invoices.append(last_invoice)

			context2=context.copy()
			context2['lang'] = partner.lang
			cr.execute("SELECT product_id, to_invoice, sum(unit_amount) " \
					"FROM account_analytic_line as line " \
					"WHERE account_id = %d " \
						"AND id IN (" + ','.join([str(x) for x in data['ids']]) + ") " \
						"AND to_invoice IS NOT NULL " \
					"GROUP BY product_id,to_invoice", (account.id,))
			for product_id,factor_id,qty in cr.fetchall():
				product = pool.get('product.product').browse(cr, uid, product_id, context2)
				if not product:
					raise wizard.except_wizard('Error', 'At least on line have no product !')
				factor_name = ''
				factor = pool.get('hr_timesheet_invoice.factor').browse(cr, uid, factor_id, context2)
				if factor.customer_name:
					factor_name = product.name+' - '+factor.customer_name
				else:
					factor_name = product.name
				if account.pricelist_id:
					pl = account.pricelist_id.id
					price = pool.get('product.pricelist').price_get(cr,uid,[pl], product_id, qty or 1.0, account.partner_id.id)[pl]
				else:
					price = 0.0

				taxes = product.taxes_id
				taxep = account.partner_id.property_account_tax
				if not taxep.id:
					tax = [x.id for x in taxes or []]
				else:
					tax = [taxep.id]
					for t in taxes:
						if not t.tax_group==taxep.tax_group:
							tax.append(t.id)

				account_id = product.product_tmpl_id.property_account_income.id or product.categ_id.property_account_income_categ.id

				curr_line = {
					'price_unit': price,
					'quantity': qty,
					'discount':factor.factor,
					'invoice_line_tax_id': [(6,0,tax )],
					'invoice_id': last_invoice,
					'name': factor_name,
					'product_id': data['form']['product'] or product_id,
					'invoice_line_tax_id': [(6,0,tax)],
					'uos_id': product.uom_id.id,
					'account_id': account_id,
					'account_analytic_id': account.id,
				}

				#
				# Compute for lines
				#
				cr.execute("SELECT * FROM account_analytic_line WHERE account_id = %d and id IN (%s) AND product_id=%d and to_invoice=%d" % (account.id, ','.join(map(str,data['ids'])), product_id, factor_id))
				line_ids = cr.dictfetchall()
				note = []
				for line in line_ids:
					# set invoice_line_note
					details = []
					if data['form']['date']:
						details.append(line['date'])
					if data['form']['time']:
						details.append("%s %s" % (line['unit_amount'], pool.get('product.uom').browse(cr, uid, [line['product_uom_id']])[0].name))
					if data['form']['name']:
						details.append(line['name'])
					#if data['form']['price']:
					#	details.append(abs(line['amount']))
					note.append(' - '.join(map(str,details)))

				curr_line['note'] = "\n".join(map(str,note))
				pool.get('account.invoice.line').create(cr, uid, curr_line)
				cr.execute("update account_analytic_line set invoice_id=%d WHERE account_id = %d and id IN (%s)" % (last_invoice,account.id, ','.join(map(str,data['ids']))))

		return {
			'domain': "[('id','in', ["+','.join(map(str,invoices))+"])]",
			'name': 'Invoices',
			'view_type': 'form',
			'view_mode': 'tree,form',
			'res_model': 'account.invoice',
			'view_id': False,
			'context': "{'type':'out_invoice'}",
			'type': 'ir.actions.act_window'
		}


	_create_form = """<?xml version="1.0"?>
	<form title="Invoice on analytic entries">
		<separator string="Do you want details for each line of the invoices ?" colspan="4"/>
		<field name="date"/>
		<field name="time"/>
		<field name="name"/>
		<field name="price"/>
		<separator string="Choose accounts you want to invoice" colspan="4"/>
		<field name="accounts" colspan="4"/>
		<separator string="Choose a product for intermediary invoice" colspan="4"/>
		<field name="product"/>
	</form>"""

	_create_fields = {
		'accounts': {'string':'Analytic Accounts', 'type':'many2many', 'required':'true', 'relation':'account.analytic.account'},
		'date': {'string':'Date', 'type':'boolean'},
		'time': {'string':'Time spent', 'type':'boolean'},
		'name': {'string':'Name of entry', 'type':'boolean'},
		'price': {'string':'Cost', 'type':'boolean'},
		'product': {'string':'Product', 'type':'many2one', 'relation': 'product.product'},
	}

	states = {
		'init' : {
			'actions' : [_get_accounts], 
			'result' : {'type':'form', 'arch':_create_form, 'fields':_create_fields, 'state': [('end','Cancel'),('create','Create invoices')]},
		},
		'create' : {
			'actions' : [],
			'result' : {'type':'action', 'action':_do_create, 'state':'end'},
		},
	}
invoice_create('hr.timesheet.invoice.create')
