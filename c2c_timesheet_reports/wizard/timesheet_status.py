# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) Camptocamp SA
# Author: Arnaud Wüst
#
#
#    This file is part of the c2c_timesheet_report module
#
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

import wizard
#from copy import copy
import pooler
import time


_define_filters_form = '''<?xml version="1.0"?>
    <form string="timesheet Status" width="400">
        <group colspan="4" col="4" string="Parameter">
            <separator string="End Date (display the 5 timesheets previous to this date )" colspan="4"/>
            <field name="date" colspan="4" nolabel="1" width="400" />
        </group>

        <group colspan="4" col="4" string="Filter">
            <separator string="Filter by a Company (leave empty to select all companies)" colspan="4"/>
            <field name="company" colspan="4" nolabel="1"/>
            <newline/>
        </group>
    </form>'''


_define_filters_fields = {
        'company': {'string':'Company', 'type':'many2one', 'relation':'res.company'}, 
        'date': {'string':'End Date', 'type':'date',  'default':lambda *a: time.strftime('%Y-%m-%d'), 'required':True}
        }


class wiz_timesheet_status(wizard.interface):
    

    def _get_companies_ids(self, cr, uid, data, context):       
        """ return the companies list to print. either selected in the wizard's first form that match the criterias, or the list of all companies """

        pool = pooler.get_pool(cr.dbname)
        company_object = pool.get('res.company')      
        
        
        #values from the form
        companies_ids = []
        if 'company' in data['form'] and data['form']['company'] <> False:
            companies_ids.append(data['form']['company'])
        
        #no company selected in the first form
        if len(companies_ids) == 0: 
            companies_ids = company_object.search(cr, uid, [], context=context)
                        
        values = { 'ids': companies_ids }
        return values


    states = {
        'init' : {
            'actions' : [], 
            'result' : {'type':'form', 'arch':_define_filters_form, 'fields':_define_filters_fields, 'state': [('end','Cancel'),('print','Print Status')]},
        },
        'print' : {
            'actions': [_get_companies_ids],
            'result': {'type':'print', 'report':'c2c_timesheet_reports.timesheet_status', 'get_id_from_action': True, 'state':'end'},            
        },
                    
    }
    
    
wiz_timesheet_status('c2c_timesheet_reports.timesheet_status');    
