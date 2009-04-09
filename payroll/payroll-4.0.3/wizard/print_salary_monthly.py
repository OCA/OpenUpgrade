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

import wizard
import time

_date_form = '''<?xml version="1.0"?>
<form string="Select employee and salary month">
    <separator string="Salary Slip Information" colspan="4"/>
    <field name="employee"/>
    <field name="month"/>
    <field name="year"/>    
</form>'''

_date_fields = {
    'employee': {'string':'Employee', 'type':'many2one', 'relation':'hr.employee', 'required':True},
    'month': {'string':'Month', 'type':'integer', 'default':lambda *a: time.gmtime()[1], 'required':True},
    'year': {'string':'Year', 'type':'integer', 'default':lambda *a: time.gmtime()[0], 'required':True},
}

class wiz_attendance(wizard.interface):
    states = {
        'init': {
            'actions': [],
            'result': {'type': 'form', 'arch':_date_form, 'fields':_date_fields, 'state':[('print','Print Salary Slip'),('end','Cancel') ]}
        },
        'print': {
            'actions': [],
            'result': {'type': 'print', 'report': 'payroll.salary.month', 'state':'end'}
        }
    }
wiz_attendance('payroll.salary.month.report')

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

