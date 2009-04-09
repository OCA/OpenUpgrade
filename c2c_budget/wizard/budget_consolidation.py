# -*- coding: utf-8 -*- 
##############################################################################
#
# Copyright (c) Camptocamp SA - http://www.camptocamp.com
# Author: Arnaud Wüst
#
#    This file is part of the c2c_budget module
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
#############################################################################

import wizard
import netsvc
import pooler


class wiz_budget_consolidation(wizard.interface):
    """ this wizard display options to print the budget consolidation report """

    def _init_fields(self, cr, uid, data, context):
        """ init the form's fields """

        budget_obj = pooler.get_pool(cr.dbname).get('c2c_budget')
        version_obj = pooler.get_pool(cr.dbname).get('c2c_budget.version')            
        
        res = {}

        #we come from budget
        if data['model'] == 'c2c_budget':
            
            #init version and version 2 with the 2 first versions
            if len(data['ids']) == 1:
                budget = budget_obj.browse(cr, uid, data['ids'][0])
                res['versions'] = [x.id for x in budget.budget_version_ids][:10]
                
        #we come from versions
        elif data['model'] == 'c2c_budget.version':
            
            res['versions'] = data['ids'][:10]

        
        version_obj = pooler.get_pool(cr.dbname).get('c2c_budget.version')            
        version = version_obj.browse(cr, uid, res['versions'][0])
        res['currency'] = version.currency_id.id
      
        return res   

    
    def _get_budget_lines(self, cr, uid, data, context):
        """ retrieve lines to work on """
        
        #check there is at least one version selected
        if len(data['form']['versions'][0][2]) == 0:
            raise wizard.except_wizard('Versions Missing', "Select at least on version to run this report")

        #check there is max 10 versions
        if len(data['form']['versions'][0][2]) > 10:
            raise wizard.except_wizard('Too Many Versions', "Select at most 10 versions of the same budget")

                    
        #check all versions belong to the same budget
        version_obj = pooler.get_pool(cr.dbname).get('c2c_budget.version')            
        versions = version_obj.browse(cr, uid, data['form']['versions'][0][2], context=context)
        budget_id = versions[0].budget_id.id
        for v in versions:
            if budget_id != v.budget_id.id:
                raise wizard.except_wizard('Incompatible Versions', "The selected versions do not belong to the same budget. Select only versions of the same budget to run the report")
                
            
                        
        #find lines to work on
        line_obj = pooler.get_pool(cr.dbname).get('c2c_budget.line')
        period_obj = pooler.get_pool(cr.dbname).get('account.period')
        
        criteria = [('budget_version_id', 'in', data['form']['versions'][0][2])]
        if len(data['form']['periods'][0][2]) > 0:
            criteria.append(('period_id', 'in', data['form']['periods'][0][2]))
        
        line_ids = line_obj.search(cr, uid, criteria, context=context)
        
        values = {'ids': line_ids
                  }    
        
        return values
        
    _form = """<?xml version="1.0"?>
    <form string="Budget Consolidation" width="600">
        
        <separator string="Select Versions (max 10 versions)" colspan="4"/>
        <field name="versions" colspan="4" nolabel="1" width="600" height="200"/>
        <newline/>
        <field name="currency" />
        <newline/>
        <separator string="Select Periods (empty for all)" colspan="4" />
        <field name="periods" colspan="4"  nolabel="1" height="200"/>
    </form>"""

    _fields = {
        'versions': {'string':'Versions', 'type':'many2many', 'relation':'c2c_budget.version', 'required':True },
        'currency': {'string':'Currency', 'type':'many2one',  'relation':'res.currency',       'required':True },
        'periods':  {'string':'Periods',  'type':'many2many', 'relation': 'account.period'}, 
    }
        
    states = {
    
        'init' : {
            'actions':[_init_fields],
            'result' : {'type':'form', 'arch':_form, 'fields':_fields, 'state': [('end','Cancel'),('print','Print')]},
        },
        'print' : {
            'actions' : [_get_budget_lines],
            'result' : {'type':'print', 'report':'budget_consolidation', 'get_id_from_action':True, 'state':'end'},
        },

    }
    
    
wiz_budget_consolidation('budget.consolidation')