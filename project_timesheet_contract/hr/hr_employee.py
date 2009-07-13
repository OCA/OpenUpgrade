from osv import osv,fields
from datetime import datetime

class hr_employee(osv.osv):
    _name = "hr.employee"
    _inherit = "hr.employee"
    def onchange_cost_based_on(self, cr, uid, ids, cost_based_on, contract_ids, product_id):
        if cost_based_on == 'contract':
            sql_req= '''
                SELECT -c.wage * cwt.factor_type / p.factor_days as hourlywage
                FROM hr_contract c
                  LEFT JOIN hr_employee emp on (c.employee_id=emp.id)
                  LEFT JOIN hr_contract_wage_type cwt on (cwt.id = c.wage_type_id)
                  LEFT JOIN hr_contract_wage_type_period p on (cwt.period_id = p.id)
                WHERE
                  (emp.user_id=%s) AND
                  (date_start <= %s) AND
                  (date_end IS NULL OR date_end >= %s)
                LIMIT 1
                '''
            cr.execute(sql_req, (uid, str(datetime.now())[:10], str(datetime.now())[:10]))
            contract_info = cr.dictfetchone()
            if not contract_info:
                raise osv.except_osv(_('Error !'), _('No valid contract found'))
        else:
            if not product_id:
                raise osv.except_osv(_('Error !'), _('No product selected'))
        return {} 
    
    _columns = {
        'cost_based_on':fields.selection([('contract', 'Contract'), ('product_cost', 'Product Cost')], 'Cost Based On',required=True)
    }
hr_employee()
