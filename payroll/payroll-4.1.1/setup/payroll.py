# -*- encoding: utf-8 -*-

from mx import DateTime
import time

from osv import fields, osv

class payroll_setup(osv.osv):
    _name = "payroll.setup"
    _description = "Payroll Setup"
    _columns = {
        'payroll_prcess_date': fields.date('Payroll Processing Date'),
        'name' : fields.char('Teamplate Name', size=32, required=True),
        'branch_code' : fields.char('Branch Code', size=32),
        'cc_code' : fields.char('Cost Center Code', size=32),
        
        'ca_exempted' : fields.float('Conveyance Allowance Exempted', digits=(12,2) ),
        'cea_exempted' : fields.float('Child Education Allowance Exempted', digits=(12,2) ),
        'cha_exempted' : fields.float('Child Hostel Allowance Exempted', digits=(12,2) ),
        'max_child' : fields.integer('Maximim number of children applicable'),
        'sr_relaxation' : fields.float('Relaxation for Sr. Citizens', digits=(12,2) ),
        'fem_relaxation' : fields.float('Relaxation for female', digits=(12,2) ),
        'sr_age' : fields.integer('Eligible age for Sr. citizen'),
        'edu_cess' : fields.float('Education cess', digits=(12,2) ),
        }
    _defaults = {
        }
    _order = 'name desc'
    
payroll_setup()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

