# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2006 TINY SPRL. (http://tiny.be) All Rights Reserved.
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
from osv import osv
import pooler

class order(report_sxw.rml_parse):
	def __init__(self, cr, uid, name, context):
		super(order, self).__init__(cr, uid, name, context)

		user = pooler.get_pool(cr.dbname).get('res.users').browse(cr,uid,uid)
		partner= user.company_id.partner_id
		

		self.localcontext.update({
			'time': time,
			'disc': self.discount,
			'net': self.netamount,
			'address': partner.address and partner.address[0] or False,
		})
			 
	def netamount(self,order_line_id):
		sql = 'select (qty*price_unit) as net_price from pos_order_line where id = %d '
		self.cr.execute(sql%(order_line_id))
		res=self.cr.fetchone();
		return res[0];

	def discount(self,order_id):
		sql = 'select discount, price_unit,qty from pos_order_line where order_id  = %d '
		self.cr.execute(sql%(order_id))
		res=self.cr.fetchall();
		sum = 0;
		for r in res:
			if r[0]!=0:
				sum = sum +(r[2] * (r[0]*r[1]/100))
		return sum;
		
report_sxw.report_sxw('report.pos.receipt','pos.order','addons/pos/report/pos_receipt.rml',parser=order,header=False)

