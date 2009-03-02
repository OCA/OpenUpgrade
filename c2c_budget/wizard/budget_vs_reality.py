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
##############################################################################

import wizard
import netsvc
import pooler
from tools.misc import UpdateableStr

arch = UpdateableStr()

_form_header = """<?xml version="1.0"?>
<form string="Budget Vs. Reality" width="600">
    
    <separator string="Select periods (empty for all)" colspan="4"/>
    <field name="periods" colspan="4" nolabel="1" width="600" height="200"/>
    <newline/> 
    """
        
_form_footer = """
    </form>"""


_fields = {
    'periods': {'string': 'Periods', 'type': 'many2many', 'relation': 'account.period'}, 
}



class wiz_budget_vs_reality(wizard.interface):
    """ this wizard allow to choose periods and AA split level before to display the report that compare a budget version to the reality """


    def _build_form(self, cr, uid, data, context):
        """complete the form with abstracted parts from  c2c_budget.wizard_abstraction """
        wiz_abstract_obj = pooler.get_pool(cr.dbname).get('c2c_budget.wizard_abstraction')
        
        #complete the form with the abstraction
        arch.string = _form_header + wiz_abstract_obj.budget_vs_real_get_form(cr, uid, data,context) + _form_footer
        
        #complete the fields with the abstraction
        fields = wiz_abstract_obj.budget_vs_real_get_fields(cr, uid, data,context)
        for f in fields:
            _fields[f] = fields[f]
        
        
        return {} 
                
    
    def _get_budget_lines(self, cr, uid, data, context):
        """ retrieve lines to work on """
        
        versions_ids = []
        
        #we come from budget
        if data['model'] == 'c2c_budget':
            
            #get all versions that belongs to these budgets           
            budget_obj = pooler.get_pool(cr.dbname).get('c2c_budget')
            budget = budget_obj.browse(cr, uid, data['ids'])
            for b in budget:
                
                versions_ids += [v.id for v in b.budget_version_ids]
                
        #we come from versions
        elif data['model'] == 'c2c_budget.version':
            #get all selected versions
            versions_ids = data['ids']
        
        
        criteria = [('budget_version_id', 'in', versions_ids)]
        
        if len(data['form']['periods'][0][2]) > 0:
            criteria.append(('period_id', 'in', data['form']['periods'][0][2]))
        
        line_obj = pooler.get_pool(cr.dbname).get('c2c_budget.line')
        line_ids = line_obj.search(cr, uid, criteria, context=context)
        
               
        values = {'ids': line_ids,
                  'version_ids': versions_ids}    
        
        return values
        
            
    states = {
    
        'init' : {
            'actions':[_build_form],
            'result' : {'type':'form', 'arch':arch, 'fields':_fields, 'state': [('end','Cancel'),('print','Print')]},
        },
        'print' : {
            'actions' : [_get_budget_lines],
            'result' : {'type':'print', 'report':'budget_vs_reality', 'get_id_from_action':True, 'state':'end'},
        },

    }
    
    
wiz_budget_vs_reality('budget.vs.reality')