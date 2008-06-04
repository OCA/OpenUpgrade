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

import netsvc
import time
from osv import fields, osv


class credit_line(osv.osv):
	_name = 'credit.line'
	_description = 'Credit line'

	def get_available_amount(self, cr, uid, credit_line_id, base_amount, partner_id, context={}):
		#sum the eligible amounts for translation folder + embassy folder line for this customer
		this = self.browse(cr, uid, [credit_line_id])[0]
		sum = 0
		print this.id
		list = self.pool.get('translation.folder').search(cr, uid, [('credit_line_id','=',this.id), ('partner_id', '=', partner_id)])
		for item in self.pool.get('translation.folder').browse(cr, uid, list):
			sum +=  item.awex_amount

		#list = self.pool.get('cci_missions.embassy_folder_line').search(cr, uid, [('credit_line_id','=',self.id)), ('folder_id.partner_id', '=', partner_id)])
		#for item in list:
		#	sum += item.awex_amount

		print 'customer sum: ', sum
		remaining_amount = this.customer_credit - sum
		if remaining_amount <= 0:
			return 0
		if (base_amount/2) > remaining_amount:
			return remaining_amount


		#sum the eligible amounts for translation folder + embassy folder line for all customers
		sum = 0
		list = self.pool.get('translation.folder').search(cr, uid, [('credit_line_id','=',this.id)])
		for item in self.pool.get('translation.folder').browse(cr, uid, list):
			sum += item.awex_amount

		#list = self.pool.get('cci_missions.embassy_folder_line').search(cr, uid, [('credit_line_id','=',self.id)), ('folder_id.partner_id', '=', partner_id)])
		#for item in list:
		#	sum += item.awex_amount
		print 'total sum: ', sum

		remaining_amount = this.global_credit - sum
		if remaining_amount <= 0:
			return 0
		if (base_amount/2) > remaining_amount:
			return remaining_amount
		return base_amount / 2

	_columns = {
		'name':fields.char('Name', size=32, required=True),
		'from_date':fields.date('From Date', required=True),
		'to_date':fields.date('To Date', required=True),
		'global_credit':fields.float('Global Credit', required=True),
		'customer_credit':fields.float('Customer Max Credit', required=True)
	}
credit_line()

class translation_folder(osv.osv):
	_name = 'translation.folder'
	_description = 'Translation Folder'

	def cci_translation_folder_confirmed(self, cr, uid, ids, *args):
		for id in self.browse(cr, uid, ids):
			data = {}
			data['state']='confirmed'
			if id.awex_eligible and id.partner_id.awex_eligible == 'yes':
				print 'go'
				#look for an existing credit line in the current time
				credit_line = self.pool.get('credit.line').search(cr, uid, [('from_date','<=',time.strftime('%Y-%m-%d')), ('to_date', '>=', time.strftime('%Y-%m-%d'))])
				if credit_line:
					#if there is one available: get available amount from it
					amount = self.pool.get('credit.line').browse(cr, uid,[credit_line[0]])[0].get_available_amount(cr, uid, credit_line[0], id.base_amount, id.partner_id.id)
					if amount > 0:
						data['awex_amount'] = amount
						data['credit_line_id'] =  credit_line[0]
					else:
						data['awex_eligible'] = False
			self.write(cr, uid, [id.id], data)
		return True

	_columns = {
		'name': fields.char('Name', size=32, required=True),
		'partner_id': fields.many2one('res.partner', 'Partner', required=True),
		'base_amount': fields.float('Base Amount', required=True, readonly=True, states={'draft':[('readonly',False)]}),
		'awex_eligible':fields.boolean('AWEX Eligible', readonly=True, states={'draft':[('readonly',False)]}),
		'awex_amount':fields.float('AWEX Amount', readonly=True),
		'state':fields.selection([('draft','Draft'),('confirmed','Confirmed'),('invoiced','Invoiced'),('done', 'Done'),('cancel','Cancel')],'State',readonly=True),
		'credit_line_id': fields.many2one('credit.line', 'Credit Line', readonly=True),
		'invoice_id': fields.many2one('account.invoice', 'Invoice'),
		'purchase_order': fields.many2one('purchase.order', 'Purchase Order'),
	}
	_defaults = {
		'state' : lambda *a : 'draft',
	}
translation_folder()

class letter_credence(osv.osv):
	_name = 'letter.credence'
	_description = 'Letter of Credence'
	_columns = {
		'emission_date':fields.date('Emission Date', required=True),
		'asked_amount':fields.float('Asked Amount', required=True)
	}
letter_credence()

class res_partner(osv.osv):
	_inherit = 'res.partner'
	_description = 'Partner'
	_columns = {
		'awex_eligible':fields.selection([('unknown','Unknown'),('yes','Yes'),('no','No')], "AWEX Eligible"),
	}
	_defaults = {
		'awex_eligible' : lambda *a : 'unknown',
	}
res_partner()

class translation_billing_line(osv.osv):
	_inherit = 'cci_missions.embassy_folder_line'
	_description = 'Translation Billing Line'
	_columns = {
		'awex_eligible':fields.boolean('AWEX Eligible'),
		'awex_amount':fields.float('AWEX Amount')
	}
translation_billing_line()
