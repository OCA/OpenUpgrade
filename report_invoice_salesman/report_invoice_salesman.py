##############################################################################
#
# Copyright (c) 2004-2006 TINY SPRL. (http://tiny.be) All Rights Reserved.
#
# $Id: sale.py 1005 2005-07-25 08:41:42Z nicoe $
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

import time
import mx.DateTime

class report_invoice_salesman_forecast(osv.osv):
	_name = "report_invoice_salesman.forecast"
	_description = "Sales Forecast"
	_columns = {
		'name': fields.char('Sales Forecast', size=32, required=True),
		'user_id': fields.many2one('res.users', 'Responsible', required=True),
		'date_from':fields.date('Start Period', required=True),
		'date_to':fields.date('End Period', required=True),
		'line_ids': fields.one2many('report_invoice_salesman.forecast.line', 'forecast_id', 'Forecast lines'),
	}
	_defaults = {
		'name': lambda *a: time.strftime('%Y-%m-%d'),
		'date_from': lambda *a: time.strftime('%Y-%m-01'),
		'date_to': lambda *a: (mx.DateTime.now()+mx.DateTime.RelativeDateTime(months=1,day=1,days=-1)).strftime('%Y-%m-%d'),
		'user_id': lambda self,cr,uid,c: uid
	}
	_order = 'date_from desc'
report_invoice_salesman_forecast()

class report_invoice_salesman_forecast_line(osv.osv):
	_name = "report_invoice_salesman.forecast.line"
	_description = "Forecast Line"
	_rec_name = 'user_id'
	_columns = {
		'forecast_id': fields.many2one('report_invoice_salesman.forecast', 'Forecast', required=True, ondelete='cascade'),
		'category_id':fields.many2one('product.category', 'Product Category', required=True),
		'user_id': fields.many2one('res.users', 'Salesman'),
		'amount': fields.float('Amount'),
		'margin': fields.float('Margin'),
		'note':fields.text('Note', size=64),
	}
	_order = 'user_id,category_id'
report_invoice_salesman_forecast_line()


class report_invoice_salesman_forecast_stat_global(osv.osv):
	_name = "report_invoice_salesman.forecast.stat.global"
	_description = "Forecasts by Salesman"
	_rec_name = 'date_from'
	_auto = False
	_log_access = False
	def _sum_margin_real(self, cr, uid, ids, name, args, context):
		result = {}
		for line in self.browse(cr, uid, ids, context):
			query = '''select 
					sum(l.price_unit * l.quantity * ((100-l.discount)/100.0) - l.quantity * t.standard_price) 
				from account_invoice_line l 
				left join account_invoice i on (l.invoice_id=i.id)
				left join product_product p on (l.product_id=p.id)
				left join product_template t on (p.product_tmpl_id=t.id)
				where 
					i.state in ('open','done') and
					i.date_invoice>=%s and 
					i.date_invoice<=%s'''
			query2 = [line.date_from, line.date_to]
			if line.user_id:
				query += ' and i.user_id=%d'
				query2.append(line.user_id.id)
			cr.execute(query, query2)
			result[line.id] = cr.fetchone()[0]
		return result
	def _sum_amount_real(self, cr, uid, ids, name, args, context):
		result = {}
		for line in self.browse(cr, uid, ids, context):
			query = '''select 
					sum(l.price_unit * l.quantity * ((100-l.discount)/100.0)) 
				from account_invoice_line l 
				left join account_invoice i on (l.invoice_id=i.id)
				left join product_product p on (l.product_id=p.id)
				left join product_template t on (p.product_tmpl_id=t.id)
				where 
					i.state in ('open','done') and
					i.date_invoice>=%s and 
					i.date_invoice<=%s'''
			query2 = [line.date_from, line.date_to]
			if line.user_id:
				query += ' and i.user_id=%d'
				query2.append(line.user_id.id)
			cr.execute(query, query2)
			result[line.id] = cr.fetchone()[0]
		return result
	_columns = {
		'user_id': fields.many2one('res.users', 'Salesman'),
		'amount': fields.float('Amount'),
		'margin': fields.float('Margin'),
		'forecast_id': fields.many2one('report_invoice_salesman.forecast', 'Forecast'),
		'sum_amount': fields.function(_sum_amount_real, method=True, string='Amount Real'),
		'sum_margin': fields.function(_sum_margin_real, method=True, string='Margin Real'),
		'manager_id': fields.many2one('res.users', 'Responsible', required=True),
		'date_from':fields.date('Start Period', required=True),
		'date_to':fields.date('End Period', required=True),
	}
	def init(self, cr):
		cr.execute("""create or replace view report_invoice_salesman_forecast_stat_global as (
			select
				min(l.id) as id,
				f.date_from as date_from,
				f.date_to as date_to,
				f.id as forecast_id,
				f.user_id as manager_id,
				l.user_id as user_id,
				sum(l.amount) as amount,
				sum(l.margin) as margin
			from
				report_invoice_salesman_forecast f
			left join
				report_invoice_salesman_forecast_line l on (l.forecast_id=f.id)
			group by 
				f.id, f.user_id, 
				l.user_id, f.date_from, f.date_to
		) """)
report_invoice_salesman_forecast_stat_global()

class report_invoice_salesman_forecast_stat(osv.osv):
	_name = "report_invoice_salesman.forecast.stat"
	_description = "Sales Forecasts"
	_rec_name = 'date_from'
	_auto = False
	_log_access = False
	def _sum_margin_real(self, cr, uid, ids, name, args, context):
		result = {}
		for line in self.browse(cr, uid, ids, context):
			cids = self.pool.get('product.category').search(cr, uid, [
				('parent_id','child_of',[line.category_id.id])
			], context=context)
			query = '''select 
					sum(l.price_unit * l.quantity * ((100-l.discount)/100.0) - l.quantity * t.standard_price) 
				from account_invoice_line l 
				left join account_invoice i on (l.invoice_id=i.id)
				left join product_product p on (l.product_id=p.id)
				left join product_template t on (p.product_tmpl_id=t.id)
				where 
					t.categ_id in ('''+','.join(map(str,cids))+''') and 
					i.state in ('open','done') and
					i.date_invoice>=%s and 
					i.date_invoice<=%s'''
			query2 = [line.date_from, line.date_to]
			if line.user_id:
				query += ' and i.user_id=%d'
				query2.append(line.user_id.id)
			cr.execute(query, query2)
			result[line.id] = cr.fetchone()[0]
		return result
	def _sum_amount_real(self, cr, uid, ids, name, args, context):
		result = {}
		for line in self.browse(cr, uid, ids, context):
			cids = self.pool.get('product.category').search(cr, uid, [ ('parent_id','child_of',[line.category_id.id]) ], context=context)
			query = '''select 
					sum(l.price_unit * l.quantity * ((100-l.discount)/100.0)) 
				from account_invoice_line l 
				left join account_invoice i on (l.invoice_id=i.id)
				left join product_product p on (l.product_id=p.id)
				left join product_template t on (p.product_tmpl_id=t.id)
				where 
					t.categ_id in ('''+','.join(map(str,cids))+''') and 
					i.state in ('open','done') and
					i.date_invoice>=%s and 
					i.date_invoice<=%s'''
			query2 = [line.date_from, line.date_to]
			if line.user_id:
				query += ' and i.user_id=%d'
				query2.append(line.user_id.id)
			cr.execute(query, query2)
			result[line.id] = cr.fetchone()[0]
		return result
	_columns = {
		'category_id':fields.many2one('product.category', 'Product Category', required=True),
		'user_id': fields.many2one('res.users', 'Salesman'),
		'amount': fields.float('Amount'),
		'margin': fields.float('Margin'),
		'forecast_id': fields.many2one('report_invoice_salesman.forecast', 'Forecast'),
		'sum_amount': fields.function(_sum_amount_real, method=True, string='Amount Real'),
		'sum_margin': fields.function(_sum_margin_real, method=True, string='Margin Real'),
		'manager_id': fields.many2one('res.users', 'Responsible', required=True),
		'date_from':fields.date('Start Period', required=True),
		'date_to':fields.date('End Period', required=True),
	}
	def init(self, cr):
		cr.execute("""create or replace view report_invoice_salesman_forecast_stat as (
			select
				l.id as id,
				f.date_from as date_from,
				f.date_to as date_to,
				f.id as forecast_id,
				f.user_id as manager_id,
				l.user_id as user_id,
				l.amount as amount,
				l.category_id as category_id,
				l.margin as margin
			from
				report_invoice_salesman_forecast f
			left join
				report_invoice_salesman_forecast_line l on (l.forecast_id=f.id)
		) """)
report_invoice_salesman_forecast_stat()
