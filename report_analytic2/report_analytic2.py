# -*- coding: utf-8 -*- 
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
from osv import osv, fields

class report_analytic_by_year(osv.osv):
    _name='report.analytic.by.year'
    _description = "Reporting by accounts/ by year"
    _rec_name= "year"
    _auto=False
    _columns = {
        'year': fields.integer('Year',readonly=True),
        'amount': fields.float('Amount', readonly=True, digits=(16,2)),
        }

    def init(self, cr):
        cr.execute("""
            CREATE OR REPLACE VIEW report_analytic_by_year as (
            SELECT
                min(inv.id) as id,
                sum(inv.amount_total) as amount,
                date_part('year', inv.date_invoice) as year
            FROM
                account_invoice inv
            GROUP BY  date_part('year', inv.date_invoice))

                """)

report_analytic_by_year()

class report_analytic_by_month(osv.osv):
    _name='report.analytic.by.month'
    _description = "Reporting by accounts/ by month"
    _rec_name= "month"
    _auto=False
    _columns = {
        'month': fields.integer('Month',readonly=True),
        'year': fields.integer('Year',readonly=True),
        'amount': fields.float('Amount', readonly=True, digits=(16,2)),
        }

    def init(self, cr):
        cr.execute("""
            CREATE OR REPLACE VIEW report_analytic_by_month as (
            SELECT
                min(inv.id) as id,
                sum(inv.amount_total) as amount,
                date_part('month', inv.date_invoice) as month,
                date_part('year', inv.date_invoice) as year
            FROM
                account_invoice inv
            GROUP BY date_part('month', inv.date_invoice), date_part('year', inv.date_invoice))

                """)

report_analytic_by_month()

class report_analytic_by_product(osv.osv):
    _name='report.analytic.by.product'
    _description = "Reporting by accounts/ by product"
    _rec_name= "name"
    _auto=False
    _columns = {
        'name': fields.char('Product Name',readonly=True, size=64),
        'year': fields.integer('Year',readonly=True),
        'amount': fields.float('Amount', readonly=True, digits=(16,2)),
        }

    def init(self, cr):
        cr.execute("""
            CREATE OR REPLACE VIEW report_analytic_by_product as (
                SELECT
                  min(inv.id) as id,
                  sum(inv.amount_total) as amount,
                  max(t.name) as name,
                  date_part('year'::text, inv.date_invoice) as year
                FROM
                  account_invoice_line l
                  inner join account_invoice inv
                    on inv.id = l.invoice_id
                  inner join product_product p
                    on p.id=l.product_id
                  inner join product_template t
                    on t.id=p.product_tmpl_id
                GROUP BY t.name, date_part('year', inv.date_invoice)
                )
            """)
report_analytic_by_product()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
