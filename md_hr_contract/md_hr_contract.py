##############################################################################
#
# Copyright (c) 2005-2006 TINY SPRL. (http://tiny.be) All Rights Reserved.
#
# $Id: hr.py 7208 2007-08-31 13:02:16Z ced $
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