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


import time
from report import report_sxw

class salary_print(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(salary_print, self).__init__(cr, uid, name, context)
        self.localcontext.update({
            'time': time,
            'lst_payelems': self._lst_payelems,
            'lst_deduc': self._lst_payelems,
            'lst_reimb': self._lst_payelems,
            'get_total': self._get_total,           
        })

    def _lst_payelems(self, employee_id, month, year, *args):
        print 'payelems:'
        self.cr.execute('select name as descr, cal_value as value, arrear, incr_id, incr_date from employee_setup_payelements where employee_id=%d and element_type=%s', (employee_id, 'payelements') )
        print 'fine'
        res = self.cr.dictfetchall()
        print 'result : ',res
        return res

    def _get_total(self, employee_id, month, year):
        return 200000

    def _lst(self, employee_id, dt_from, dt_to, max, *args):
        self.cr.execute('select name as date, create_date, action, create_date-name as delay from hr_attendance where employee_id=%d and name<=%s and name>=%s and action in (%s,%s) order by name', (employee_id, dt_to, dt_from, 'sign_in', 'sign_out'))
        res = self.cr.dictfetchall()
        for r in res:
            if r['action']=='sign_out':
                r['delay'] = - r['delay']
            temp = r['delay'].seconds
            r['delay'] = self._sign(r['delay'])
            if abs(temp) < max*60:
                r['delay2'] = r['delay']
            else:
                r['delay2'] = '/'
        return res

    def _lst_total(self, employee_id, dt_from, dt_to, max, *args):
        self.cr.execute('select name as date, create_date, action, create_date-name as delay from hr_attendance where employee_id=%d and name<=%s and name>=%s and action in (%s,%s)', (employee_id, dt_to, dt_from, 'sign_in', 'sign_out'))
        res = self.cr.dictfetchall()
        if not res:
            return ('/','/')
        total = 0
        total2 = 0
        for r in res:
            if r['action']=='sign_out':
                r['delay'] = - r['delay']
            total += r['delay']
            if abs(r['delay'].seconds) < max*60:
                total2 += r['delay']

        return (self._sign(total),total2 and self._sign(total2))

report_sxw.report_sxw('report.payroll.salary.month', 'hr.employee', 'addons/payroll4/report/salary_month.rml',parser=salary_print)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

