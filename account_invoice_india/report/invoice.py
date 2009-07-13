##############################################################################
#
# Copyright (c) 2005-2006 TINY SPRL. (http://tiny.be) All Rights Reserved.
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
from report import report_sxw
from tools import amount_to_text_en

class account_invoice_tax_retail(report_sxw.rml_parse):
	def __init__(self, cr, uid, name, context):
		super(account_invoice_tax_retail, self).__init__(cr, uid, name, context)
		self.localcontext.update({
			'time': time,
			'title': self.getTitle,
			'convert':self.convert,
			'getShippingAddress': self.getShippingAddress,
		})
	
	def getTitle(self, invoice):
		title = '';
		if invoice.retail_tax:
			title = invoice.retail_tax[0].swapcase() + invoice.retail_tax[1:]
		return title;
	
	def convert(self,amount, cur):
		amt_en = amount_to_text_en.amount_to_text(amount,'en',cur);
		return amt_en
       
	def getShippingAddress(self,obj):
		result=[]
		res={
			 'title':'',
			 'name':'',
			 'street':'',
			 'street2':'',
			 'zip':'',
			 'city':'',
			 'state_name':'',
			 'country_name':'',
			 'email':'',
			 'phone':'',
			 'fax':'',
			 'mobile':'',
			 }
		obj_address=obj.partner_id.address
		for obj_add in obj_address:
			if obj_add.type=='delivery' or obj_add.type=='default':
				res['title']=obj_add.title
				res['name']=obj_add.name
				res['street']=obj_add.street
				res['street2']=obj_add.street2
				res['zip']=obj_add.zip
				res['city']=obj_add.city
				if obj_add.state_id:
					res['state_name']=obj_add.state_id.name
				if obj_add.country_id:
					res['country_name']=obj_add.country_id.name
				res['email']=obj_add.email
				res['phone']=obj_add.phone
				res['fax']=obj_add.fax
				res['mobile']=obj_add.mobile
				result.append(res)
		return result
		
report_sxw.report_sxw(
	'report.tax.retail.account.invoice',
	'account.invoice',
	'account_invoice_india/report/invoice.rml',
	parser=account_invoice_tax_retail,header=False
)
