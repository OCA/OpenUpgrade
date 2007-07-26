##############################################################################
#
# Copyright (c) 2005 TINY SPRL. (http://tiny.be) All Rights Reserved.
#
# $Id$
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
import time
from report import report_sxw
from osv import osv

class buyer_form_report(report_sxw.rml_parse):
	def __init__(self, cr, uid, name, context):
		super(buyer_form_report, self).__init__(cr, uid, name, context)
		self.localcontext.update({
			'time': time,
			'sum_taxes': self.sum_taxes,
	})

	def sum_taxes(self, auction_id,obj_price):

		 print "Auction Id :",auction_id
		 buyer_cost = self.pool.get('auction.dates').read(self.cr,self.uid,[auction_id],['buyer_costs'])[0]
		 print "Buyer Cost :",buyer_cost['buyer_costs']
		 total_amount = 0.0
		 for id in buyer_cost['buyer_costs'] :
		 	print "Pooler",self.pool.get('account.tax')
		 	amount = self.pool.get('account.tax').read(self.cr,self.uid,[id],['amount'])[0]['amount']
		 	print  "Amoubnt :",amount
		 	total_amount += (amount*obj_price)


		 return total_amount


report_sxw.report_sxw('report.buyer_form_report', 'auction.lots', 'addons/auction/report/buyer_form_report.rml', parser=buyer_form_report)

