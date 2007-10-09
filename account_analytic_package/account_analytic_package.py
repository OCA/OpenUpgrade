# -*- coding: utf-8 -*- 
##############################################################################
#
# Copyright (c) 2004 TINY SPRL. (http://tiny.be) All Rights Reserved.
#					Fabien Pinckaers <fp@tiny.Be>
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
import operator
from osv import osv, fields

class product_product(osv.osv):
	_inherit = "product.product"
	_columns = {
		'package_weight': fields.float('Package Weight', digits=(16,2)),
	}
	_defaults = {
		'package_weight': lambda *args: 0.0
	}
product_product()

class crm_case_section(osv.osv):
	_inherit = "crm.case.section"
	_columns = {
		'package_weight': fields.float('Package Weight', digits=(16,2)),
	}
	_defaults = {
		'package_weight': lambda *args: 0.0
	}
crm_case_section()

class account_analytic_line_package(osv.osv):
	_name = "account.analytic.line.package"
	_auto = False
	def init(self, cr):
		cr.execute("""
			CREATE OR REPLACE VIEW account_analytic_line_package AS (
				select
					l.id,
					l.name,
					l.date,
					a.partner_id,
					a.id as account_id,
					l.product_id,
					p.package_weight as unit_weight,
					p.package_weight*l.unit_amount as total_weight,
					l.unit_amount 
				from 
					account_analytic_line l 
				left join 
					account_analytic_account a on (l.account_id=a.id) 
				left join 
					product_product p on (p.id=l.product_id) 
				where 
					l.product_id is not null and
					p.package_weight<>0
			)
		""")
	_columns = {
		'name': fields.char('Name', size=128, readonly=True, select=1),
		'date': fields.date('Date', readonly=True, select=1),
		'partner_id': fields.many2one('res.partner', 'Partner', readonly=True),
		'account_id': fields.many2one('account.analytic.account', 'Account', readonly=True),
		'product_id': fields.many2one('product.product', 'Product', select=2, readonly=True),
		'unit_amount': fields.float('Quantity', readonly=True),
		'unit_weight': fields.float('Unit Weight', readonly=True),
		'total_weight': fields.float('Total Weight', readonly=True),
	}
account_analytic_line_package()

class account_analytic_line_package_month(osv.osv):
	_name = "account.analytic.line.package.month"
	_auto = False
	def init(self, cr):
		cr.execute("""
			CREATE OR REPLACE VIEW account_analytic_line_package_month AS (
				select
					min(l.id) as id,
					substring(l.date,0,8)||'-01' as name,
					a.partner_id,
					l.product_id,
					sum(p.package_weight*l.unit_amount) as total_weight,
					sum(case when p.package_weight>0 then p.package_weight*l.unit_amount else 0 end) as total_activity,
					sum(case when p.package_weight<0 then -p.package_weight*l.unit_amount else 0 end) as total_service
				from 
					account_analytic_line l 
				left join 
					account_analytic_account a on (l.account_id=a.id) 
				left join 
					product_product p on (p.id=l.product_id) 
				where 
					l.product_id is not null and
					p.package_weight<>0
				group by
					l.product_id,
					a.partner_id,
					substring(l.date,0,8)
			)
		""")
	_columns ={
		'name': fields.date('Date', readonly=True, select=1),
		'partner_id': fields.many2one('res.partner', 'Partner', readonly=True),
		'product_id': fields.many2one('product.product', 'Product', select=2, readonly=True),
		'total_weight': fields.float('Total Weight', readonly=True),
		'total_activity': fields.float('Total Activity', readonly=True),
		'total_service': fields.float('Total Service', readonly=True),
	}
account_analytic_line_package_month()
