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

class payroll_setup_reimbursements(osv.osv):
    _name = "payroll.setup.reimbursements"
    _description = "Reimbursements"
    _columns = {
            'name' : fields.char('Element ID', size=32, required=True),
            'element_type' : fields.many2one("payroll.setup.elements", 'Element Type', domain=[('category','=','reimbursements')]),
            'description' : fields.char('Description', size=32),
            #'element_specific' : fields.boolean("Pay Element Specific"),
            #'taxable' : fields.boolean("Taxable"),
            #'attendance' : fields.boolean("Attendance Specific"),
            'monthly_variable' : fields.boolean("Monthly Variable"),
            'emp_wise_posting' : fields.boolean("Employee Wise Posting"),
            #'dependent_on' : fields.many2one("payroll.setup.payelements", "Pay Element"),
            #'formulae' : fields.selection([('percent','PERCENT'),('addition','ADDITION'),('subtraction','SUBTRACTION'),('multiplication','MULTIPLICATION')], 'Formulae'),
            'value' : fields.float("Max. Value", digits=(12,2)),
        }
    _defaults = {
            #'attendance' : lambda *a: True,
        }
    _order = 'name desc'
    
payroll_setup_reimbursements()


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

