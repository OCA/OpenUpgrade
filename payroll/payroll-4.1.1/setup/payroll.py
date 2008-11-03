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

