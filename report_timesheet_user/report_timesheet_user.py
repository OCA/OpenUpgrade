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
import tools.sql


class  report_timesheet_user_user(osv.osv):
    _name = "report.timesheet.user.user"
    _description = "Tasks by user and company"
    _auto = False
    _columns = {
        'name': fields.date('Month', readonly=True),
        'company_id' : fields.many2one('res.company','Company Name',readonly=True),
        'user_company_id': fields.many2one('res.company', "User's Company",readonly=True),
        'total_hours': fields.float('Task Hours', readonly=True),
        'total_cost': fields.float('Task Cost', readonly=True),
        'user_id':fields.many2one('res.users','User',readonly=True)
    }
    def init(self, cr):
        tools.sql.drop_view_if_exists(cr, 'report_timesheet_user')
        cr.execute("""
        create or replace view report_timesheet_user_user as (
            select
                min(l.id) as id,
                to_char(l.date, 'YYYY-MM-01') as name,
                u.company_id as user_company_id,
                u.id as user_id,
                a.company_id as company_id,
                sum(amount) as total_cost,
                sum(unit_amount) as total_hours
          from
                hr_analytic_timesheet t
                  left join account_analytic_line l on (t.line_id=l.id)
                  left join res_users u on (l.user_id=u.id)
                  left join account_analytic_account a on (l.account_id=a.id)
                  group by to_char(l.date, 'YYYY-MM-01'), u.company_id,a.company_id,u.id
        )
       """)
report_timesheet_user_user()

class  report_timesheet_user (osv.osv):
    _name = "report.timesheet.user"
    _description = "Tasks by company"
    _auto = False
    _columns = {
        'name': fields.date('Month', readonly=True),
        'company_id' : fields.many2one('res.company','Company Name',readonly=True),
        'user_company_id': fields.many2one('res.company', "User's Company",readonly=True),
        'total_hours': fields.float('Task Hours', readonly=True),
        'total_cost': fields.float('Task Cost', readonly=True),
        #'user_id':fields.many2one('res.user','User',readonly=True)
    }

    def init(self, cr):
        cr.execute("""
        create or replace view report_timesheet_user as (
            select
                min(l.id) as id,
                to_char(l.date, 'YYYY-MM-01') as name,
                u.company_id as user_company_id,
                a.company_id as company_id,
                sum(amount) as total_cost,
                sum(unit_amount) as total_hours
          from
                hr_analytic_timesheet t
                  left join account_analytic_line l on (t.line_id=l.id)
                  left join res_users u on (l.user_id=u.id)
                  left join account_analytic_account a on (l.account_id=a.id)
                  group by to_char(l.date, 'YYYY-MM-01'), u.company_id,a.company_id
        )
       """)
report_timesheet_user()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

