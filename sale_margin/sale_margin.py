##############################################################################
#
# Copyright (c) 2004-2006 TINY SPRL. (http://tiny.be) All Rights Reserved.
#
# $Id: partner.py 1007 2005-07-25 13:18:09Z kayhman $
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

from osv import fields,osv
import pooler
from tools import config
import time

class sale_order_line(osv.osv):
	_name = "sale.order.line"
	_inherit = "sale.order.line"
	def _product_margin(self, cr, uid, ids, field_name, arg, context):
		res = {}
		for line in self.browse(cr, uid, ids):
			res[line.id] = 0
			if line.product_id:
				res[line.id] = round((line.price_unit*line.product_uos_qty*(100.0-line.discount)/100.0) -(line.product_id.standard_price*line.product_uos_qty),2)
		return res

	_columns = {
		'margin': fields.function(_product_margin, method=True, string='Margin'),
	}
sale_order_line()

class sale_order(osv.osv):
	_name = "sale.order"
	_inherit = "sale.order"

	def _product_margin(self, cr, uid, ids, field_name, arg, context):
		id_set = ",".join(map(str, ids))
		cr.execute("""
			SELECT
				s.id,
				COALESCE(SUM(l.price_unit*l.product_uos_qty*(100-l.discount)/100.0 - t.standard_price * l.product_uos_qty),0)::decimal(16,2) AS amount
			FROM
				sale_order s
			LEFT OUTER JOIN sale_order_line l ON (s.id=l.order_id)
			LEFT JOIN product_product p ON (p.id=l.product_id)
			LEFT JOIN product_template t ON (t.id=p.product_tmpl_id)
			WHERE
				s.id IN ("""+id_set+""") GROUP BY s.id """)
		res = dict(cr.fetchall())
		return res

	_columns = {
		'margin': fields.function(_product_margin, method=True, string='Margin'),
	}
sale_order()


