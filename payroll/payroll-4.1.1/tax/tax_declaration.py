# -*- encoding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2005-2006 TINY SPRL. (http://tiny.be) All Rights Reserved.
#
# $Id: hr.py 4656 2006-11-24 09:58:42Z ced $
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

from mx import DateTime
import time

from osv import fields, osv

class tax_rebate_sections(osv.osv):
    _name = "tax.rebate.sections"
    _description = "Tax Rebate Sections"
    _columns = {
        'name': fields.char("Code", size=32),
        'description': fields.char('Description', size=32),
        #'section_type'
        'max_limit' : fields.float('Maximum Limit', digits=(12,2) ),
        'deduction_inc': fields.boolean('Deduction from income'),
        'dependency' : fields.one2many('tax.rebates', 'section_id', 'Dependent Tax Rebates'),
        }
    _defaults = {
        }
            
tax_rebate_sections()

class tax_rebates(osv.osv):
    _name = "tax.rebates"
    _description = "Tax Rebates"
    _columns = {
        'name': fields.char("Code", size=32),
        'section_id': fields.many2one('tax.rebate.sections', 'Rebate Section ID' ),
        'declaration_id': fields.many2one('employee.tax.declarations', 'Declaration ID' ),
        'description': fields.char('Description', size=32),
        }
    _defaults = {
        }
            
tax_rebates()

class employee_tax_declarations(osv.osv):
    _name = "employee.tax.declarations"
    _description = "Employee Tax Declarations"
    _columns = {
        'name': fields.char("Declaration Name", size=32),
        'employee_id': fields.many2one('hr.employee', 'Employee ID' ),
        'status': fields.selection([('pending','Pending'), ('provided','Provided')], 'Status' ),
        'rebate_code': fields.many2one('tax.rebates', 'Rebate code'),
        'description': fields.char('Description', size=32),
        'scheme_code': fields.char('Scheme Code', size=32),
        'policy_no': fields.char('Policy/Account No.', size=32),
        'premium_yr': fields.date('Premium for year'),
        'amount': fields.float('Amount', digits=(12,2)),
        'deduction_inc': fields.boolean('Deduction from income'),
        'proof_recv': fields.boolean('Proof received'),
        }
    _defaults = {
        'name' : lambda *a: 'Tax Declaration',
        'status': lambda *a: 'pending',
        }
    def onchange_rebate_code(self, cr, uid, ids, r_code):
        result = {'value':{'description': False, 'deduction_inc': False}}
        print 'r_code : ',r_code
        tax_decl = self.pool.get('tax.rebates').browse(cr, uid, r_code)
        if tax_decl.description:
            result['value']['description'] = tax_decl.description
        print 'i m here'
        if tax_decl.section_id.deduction_inc:
            result['value']['deduction_inc'] = tax_decl.section_id.deduction_inc
        return result
            
employee_tax_declarations()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

