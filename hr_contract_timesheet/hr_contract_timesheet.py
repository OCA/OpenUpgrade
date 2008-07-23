# -*- encoding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2004-2006 TINY SPRL. (http://tiny.be) All Rights Reserved.
#
# $Id: account.py 1005 2005-07-25 08:41:42Z nicoe $
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


from osv import fields, osv
import time

class hr_timesheet(osv.osv):
    _name = "hr.analytic.timesheet"
    _inherit = "hr.analytic.timesheet"
    
    def on_change_unit_amount(self, cr, uid, id, prod_id, unit_amount, unit, user_id=False, date=False, context={}):
        if not date:
            date = time.strftime('%Y-%m-%d')
        if not user_id:
            user_id = uid

        res = super(hr_timesheet, self).on_change_unit_amount(cr, uid, id, prod_id, unit_amount, unit, context)
        if user_id:
            sql_req= '''
            SELECT -c.wage * cwt.factor_type / p.factor_days as hourlywage
            FROM hr_contract c
              LEFT JOIN hr_employee emp on (c.employee_id=emp.id)
              LEFT JOIN hr_contract_wage_type cwt on (cwt.id = c.wage_type_id)
              LEFT JOIN hr_contract_wage_type_period p on (cwt.period_id = p.id)
            WHERE
              (emp.user_id=%d) AND
              (date_start <= %s) AND
              (date_end IS NULL OR date_end >= %s)
            LIMIT 1
            '''

            cr.execute(sql_req, (user_id,date,date))
            contract_info = cr.dictfetchone()
            if res and contract_info:
                res['value']['amount'] = -contract_info['hourlywage'] * unit_amount

        return res
hr_timesheet()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

