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

def _get_delegated_ids(self, cr, uid, context):
    val = self.pool.get('report_account_analytic.planning').default_get(cr, uid, ['date_from','date_to'])
    cr.execute('''select
            l.id 
        from
            report_account_analytic_planning_line l
        left join
            report_account_analytic_planning p on (l.planning_id=p.id)
        where
            l.delegate_id=%s and 
            l.user_id is NULL and
            p.date_from<=%s and
            p.date_to>=%s''', (uid, val['date_from'], val['date_to'])
    )
    res = map(lambda x: x[0], cr.fetchall())
    return self.pool.get('report_account_analytic.planning.line').read(cr, uid, res, context=context)

class delegated_field(fields.one2many):
    def set(self, cr, obj, id, field, values, user=None, context=None):
        pass
    def get(self, cr, obj, ids, name, user=None, offset=0, context=None, values=None):
        result = {}
        for planing in obj.browse(cr, user, ids, context):
            cr.execute('''select
                    l.id 
                from
                    report_account_analytic_planning_line l
                left join
                    report_account_analytic_planning p on (l.planning_id=p.id)
                where
                    l.delegate_id=%s and 
                    l.user_id is NULL and
                    p.date_from<=%s and
                    p.date_to>=%s''', (planing.user_id.id, planing.date_from, planing.date_to))
            result[planing.id] = map(lambda x: x[0], cr.fetchall())
        return result

class report_account_analytic_planning(osv.osv):
    _inherit = "report_account_analytic.planning"
    _columns = {
        'delegate_ids': delegated_field('report_account_analytic.planning.line', 'planning_id', readonly=True)
    }
    _defaults = {
        'delegate_ids': lambda self,cr, uid, ctx: _get_delegated_ids(
            self,
            cr,
            uid,
            ctx
        )
    }
report_account_analytic_planning()

class report_account_analytic_planning_line(osv.osv):
    _inherit = "report_account_analytic.planning.line"
    _columns = {
        'delegate_id': fields.many2one('res.users', 'Delegate To'),
    }
report_account_analytic_planning_line()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

