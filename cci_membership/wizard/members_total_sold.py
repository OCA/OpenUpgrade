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

form = """<?xml version="1.0"?>
<form string="Members Total Sold">
    <field name="start_date"/>
    <newline />
    <field name="end_date"/>
</form>
"""
fields = {
    'start_date': {'string':'Date1', 'type':'date','required':True},
    'end_date': {'string':'Date2', 'type':'date','required':True},
          }

class check_total(wizard.interface):
    states = {
        'init' : {
            'actions' : [],
            'result': {'type': 'form', 'arch': form, 'fields': fields, 'state':[('end','Cancel'),('print','Print')]}
        },
        'print': {
            'actions': [],
            'result': {'type':'print', 'report':'cci_membership_total_sold', 'state':'end'},
        },
    }

check_total("cci_membership.check_total_sold")
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

