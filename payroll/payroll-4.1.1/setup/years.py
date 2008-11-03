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

class payroll_setup_years(osv.osv):
    _name = "payroll.setup.years"
    _description = "Years"
    _columns = {
            'name' : fields.char('Year', size=32, required=True),
            'asses_from' : fields.date('Assessment year from'),
            'asses_to' : fields.date('To'),
            'pf_from' : fields.date('PF year from'),
            'pf_to' : fields.date('To'),
            'finance_from' : fields.date('Financial year from'),
            'finance_to' : fields.date('To'),
            'leave_from' : fields.date('Leave year from'),
            'leave_to' : fields.date('To','%m%y'),
        }
    _defaults = {
            #'attendance' : lambda *a: True,
        }
    _order = 'name desc'
    
payroll_setup_years()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

