from osv import osv,fields
import datetime
from datetime import time



class hr_contract(osv.osv):
    _description='HR Contract'
    _inherit='hr.contract'
    _columns={
            'code':fields.char('code',size=8),  
            'date_start' : fields.date('Date of appointment', required=True),
            'date_end' : fields.date('Expire date'),
            'fulltime_salary':fields.float('Full-time Salary'),
            'wage' : fields.float('Base salary', required=True),
            'bank_account_nbr':fields.char('Bank account number',size=64),
            'department_id':fields.many2one('hr.department','Department'),
            'form_of_employment': fields.selection([('temp','Temporary'),('perm', 'Permanent')],'Form of employment'),
            'extend_appointment_date':fields.date('Extend appointment from'),
            'trial_period_review':fields.date('Trial period review'),
            'function' : fields.many2one('res.partner.function', 'Position'),
            'fte':fields.float('FTE'),
            'salary_level':fields.integer('Salary level',size=64),
            'salary_grade':fields.integer('Salary grade',size=64),
            'availability_per_week':fields.one2many('md.hr.contract.availability','contract_id','Availability per week'),
              }
hr_contract()

class md_hr_contract_availability(osv.osv):
    _name='md.hr.contract.availability'
    _description='HR Contract Availability'
    _columns={
              'contract_id':fields.many2one('hr.contract','Contract'),
              'day':fields.selection([('sun','Sunday'),('mon','Monday'),('tue','Tuesday'),('wed','Wednesday'),('thu','Thursday'),('fri','Friday'),('sat','Saturday')],'Day'),
              'from_hour':fields.time('From'),
              'to_hour':fields.time('To'),
              }
    _defaults={
               'day':lambda *a:'sun'
               }

md_hr_contract_availability()

class res_partner_function(osv.osv):
    _inherit = 'res.partner.function'
    _columns = {
        'name': fields.char('Position name', size=64, required=True),
    }
res_partner_function()