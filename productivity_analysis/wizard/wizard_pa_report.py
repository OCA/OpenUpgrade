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

import time
import wizard

pa_form = '''<?xml version="1.0"?>
<form string="Select period">
    <field name="date1"/>
    <field name="date2"/>
    <field name="model"/>
    <field name="type"/>
    <field name="type2"/>
    <field name="users_id" colspan="3"/>
</form>'''

pa_fields = {
    'date1': {'string':'Start of period', 'type':'date', 'required':True, 'default': lambda *a: time.strftime('%Y-%m-01')},
    'date2': {'string':'End of period', 'type':'date', 'required':True, 'default': lambda *a: time.strftime('%Y-%m-%d')},
    'users_id': {'string':'Users', 'type':'many2many', 'relation':'res.users', 'required':True},
    'model': {'string':'Object', 'type':'selection', 'selection':[('res.partner','Partners'),('sale.order', 'Sale Order'),('account.invoice','Invoices')], 'required':True},
    'type': {'string':'Period', 'type':'selection', 'selection':[('month', 'Month'),('week','Week'),('day','Day')], 'required':True, 'default': lambda *a: 'create'},
    'type2': {'string':'Analysis Value', 'type':'selection', 'selection':[('create', 'Creations'),('update','Modifications')], 'required':True},
}

class wizard_report(wizard.interface):
    states = {
        'init': {
            'actions': [], 
            'result': {'type':'form', 'arch':pa_form, 'fields':pa_fields, 'state':[('end','Cancel'),('report','Print Analysis') ]}
        },
        'report': {
            'actions': [],
            'result': {'type':'print', 'report':'productivity_analysis.report', 'state':'end'}
        }
    }
wizard_report('productivity_analysis.models.print')


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

