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
import pooler
import time


dates_form = '''<?xml version="1.0"?>
<form string="Select period">
        <field name="sdate"/>
        <newline/>
        <field name="edate"/>
</form>'''

dates_fields ={
    'sdate': {'string':'Start Date', 'type':'date', 'required':True, 'default': lambda *a: time.strftime('%Y-01-01')},
    'edate': {'string':'End Date', 'type':'date', 'required':True, 'default': lambda *a: time.strftime('%Y-%m-%d')},
            }


class datewisecheck(wizard.interface):

    states = {
       'init': {
                    'actions': [],
                    'result': {'type':'form', 'arch':dates_form, 'fields':dates_fields, 'state':[('end','Cancel'),('report','Print')]}
        },
        'report': {
                    'actions': [],
                    'result': {'type':'print', 'report':'datereport.print', 'state':'end'}
        }
    }
datewisecheck('employee.date.check')

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

