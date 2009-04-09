# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution	
#    Copyright (C) 2004-2008 Tiny SPRL (<http://tiny.be>). All Rights Reserved
#    $Id$
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from osv import fields,osv


class report_account_analytic_planning_line(osv.osv):
    _inherit = "report_account_analytic.planning.line"
    _columns = {
        'product_id': fields.many2one('product.product', 'Job / Product', required=True),
        'date_from':fields.date('Start date'),
        'date_to':fields.date('End date'),
    }

    def onchange_product_id(self, cr, uid, id, user_id, context={}, *args):

        if (not user_id):
            return {}

        query = """SELECT p.id 
                    FROM product_product p 
                    left join hr_employee e on(p.id = e.product_id) 
                    WHERE e.user_id=%d LIMIT 1"""% user_id

        cr.execute(query)
        res = cr.dictfetchone()

        if res:
            return {'value':{'product_id': res['id']}}
        return {'value': {'product_id': False}}

report_account_analytic_planning_line()


class report_account_analytic_planning_stat_product(osv.osv):

    def _sum_amount_product(self, cr, uid, ids, name, args, context):
        result = {}
        for line in self.browse(cr, uid, ids, context):
            result[line.id] = 0.0
            if line.product_id:
                cr.execute('select sum(unit_amount) from account_analytic_line where product_id=%s and date>=%s and date<=%s', (line.product_id.id,line.planning_id.date_from,line.planning_id.date_to))
                result[line.id] = cr.fetchone()[0]
        return result

    def init(self, cr):
        cr.execute("""
            create or replace view report_account_analytic_planning_stat_product as (
                select
                    min(l.id) as id,
                    p.id as product_id,
                    sum(l.amount*u.factor) as quantity,
                    l.planning_id
                from
                    report_account_analytic_planning_line l
                left join
                    product_uom u on (l.amount_unit = u.id)
                left join
                    product_product p on (p.id=l.product_id)
                group by
                    planning_id, p.id
            )
        """)

    _name = "report_account_analytic.planning.stat.product"
    _description = "Planning product stat"
    _rec_name = 'product_id'
    _auto = False
    _log_access = False
    _columns = {
        'planning_id': fields.many2one('report_account_analytic.planning', 'Planning', required=True),
        'product_id': fields.many2one('product.product', 'Post / Product', required=True),
        'quantity': fields.float('Planned', required=True),
        'sum_amount_real': fields.function(_sum_amount_product, method=True, string='Timesheet'),
    }

report_account_analytic_planning_stat_product()


class report_account_analytic_planning(osv.osv):
    _inherit = "report_account_analytic.planning"
    _columns = {
        'stat_product_ids': fields.one2many('report_account_analytic.planning.stat.product', 'planning_id', 'Planning by Post / Product', readonly=True),
    }
report_account_analytic_planning()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

