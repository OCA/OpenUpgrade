from osv import fields, osv
import time
import datetime
import pooler
import tools

class project_work(osv.osv):
    _inherit = "project.task.work"
    _description = "Task Work"

    def create(self, cr, uid, vals, *args, **kwargs):
        obj = self.pool.get('hr.analytic.timesheet')
        vals_line = {}
        obj_task = self.pool.get('project.task').browse(cr, uid, vals['task_id'])

        emp_obj = self.pool.get('hr.employee')
        emp_id = emp_obj.search(cr, uid, [('user_id', '=', vals.get('user_id', uid))])

        if not emp_id:
            raise osv.except_osv(_('Bad Configuration !'),
                 _('No employee defined for this user. You must create one.'))
        emp = self.pool.get('hr.employee').browse(cr, uid, emp_id[0])
        if not emp.product_id:
            raise osv.except_osv(_('Bad Configuration !'),
                 _('No product defined on the related employee.\nFill in the timesheet tab of the employee form.'))

        if not emp.journal_id:
            raise osv.except_osv(_('Bad Configuration !'),
                 _('No journal defined on the related employee.\nFill in the timesheet tab of the employee form.'))

        a =  emp.product_id.product_tmpl_id.property_account_expense.id
        if not a:
            a = emp.product_id.categ_id.property_account_expense_categ.id
        vals_line['general_account_id'] = a
        vals_line['journal_id'] = emp.journal_id.id
        vals_line['name'] = '%s: %s' % (tools.ustr(obj_task.name), tools.ustr(vals['name']) or '/')
        vals_line['user_id'] = vals['user_id']
        vals_line['date'] = vals['date'][:10]
        vals_line['unit_amount'] = vals['hours']
        vals_line['account_id'] = obj_task.project_id.category_id.id
        vals_line['amount'] = 00.0
        timeline_id = obj.create(cr, uid, vals_line, {})
        if emp.cost_based_on == 'contract':
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
            cr.execute(sql_req, (uid,vals['date'][:10],vals['date'][:10]))
            contract_info = cr.dictfetchone()
            if contract_info:
                vals_line['amount'] = -contract_info['hourlywage'] * vals['hours']              
            else:               
                vals_line['amount'] = (-1) * vals['hours'] * obj.browse(cr, uid, timeline_id).product_id.standard_price
        else:
                vals_line['amount'] = (-1) * vals['hours'] * obj.browse(cr, uid, timeline_id).product_id.standard_price
        obj.write(cr, uid,[timeline_id], vals_line, {})
        vals['hr_analytic_timesheet_id'] = timeline_id
        return super(osv.osv,self).create(cr, uid, vals, *args, **kwargs)
    
project_work()