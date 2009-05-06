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
<form string="Budget lines search" height="200" width="800">
    <separator string="Choose periods (empty for all)" colspan="2"/>
    <separator string="Choose items (empty for all)" colspan="2"/>
    <field name="periods" nolabel="1" colspan="2" width="400" height="150"/>
    <field name="items" nolabel="1" colspan="2" width="400"/>"""
    
_form_footer = """</form>"""




_fields = {
    'periods': {'string':'Periods', 'type':'many2many', 'relation':'account.period'},
    'items': {'string':'Budget Items', 'type':'many2many', 'relation':'c2c_budget.item'},
}


class wiz_advanced_search(wizard.interface):
    """ this wizard provide a advanced search form for budget lines """
  
  
    def _build_form(self, cr, uid, data, context):
        """complete the form with abstracted parts from  c2c_budget.wizard_abstraction """
        
        wiz_abstract_obj = pooler.get_pool(cr.dbname).get('c2c_budget.wizard_abstraction')
        
        #complete the form with the abstraction
        arch.string = _form_header + wiz_abstract_obj.advanced_search_get_form(cr, uid, data,context) + _form_footer
        
        #complete the fields with the abstraction
        fields = wiz_abstract_obj.advanced_search_get_fields(cr, uid, data,context)
        for f in fields:
            _fields[f] = fields[f]
        return {} 
  
  
    def _get_budget_lines(self, cr, uid, data, context):
        """ retrieve lines to work on """
        
        line_obj = pooler.get_pool(cr.dbname).get('c2c_budget.line')
        
        item_obj = pooler.get_pool(cr.dbname).get('c2c_budget.item')
        anal_account_obj = pooler.get_pool(cr.dbname).get('account.analytic.account')
        
        period_ids = data['form']['periods'][0][2]
        item_ids = item_obj.get_sub_items(cr, data['form']['items'][0][2])
        
        version_ids = data['form']['versions'][0][2]
        
        anal_account_ids = anal_account_obj.get_children_flat_list(cr, uid, data['form']['analytic_accounts'][0][2])
        
        if data['form']['empty_aa_too']:
            anal_account_ids.append(False)

        #build the search criteria list
        criteria = []
        if len(item_ids) > 0:
            criteria.append(('budget_item_id', 'in', item_ids))
        if len(period_ids) > 0:
            criteria.append(('period_id', 'in', period_ids))
        if len(version_ids) > 0:
            criteria.append(('budget_version_id', 'in', version_ids))
        if len(anal_account_ids) > 0:
            criteria.append(('analytic_account_id', 'in', anal_account_ids))
        
        line_ids = line_obj.search(cr, uid, criteria)
        
        
        
        # Construct domain: if there is only one item selected, 
        # put it in the domain to improve input of lines (what is in the domain will be auto-selected)
        domain=[]
        if len(item_ids)==1:
            domain.append("('budget_item_id','=',%d)"%item_ids[0])
        elif len(item_ids) > 1:
            domain.append("('budget_item_id','in',["+','.join(map(str,item_ids))+"])")
            
        if len(period_ids)==1:
            domain.append("('period_id','=',%d)"%period_ids[0])
        elif len(period_ids) > 1:
            domain.append("('period_id','in',["+','.join(map(str,period_ids))+"])")
            
        if len(version_ids)==1:
            domain.append("('budget_version_id','=',%d)"%version_ids[0])
        elif len(version_ids) > 1:
            domain.append("('budget_version_id','in',["+','.join(map(str,version_ids))+"])")
            
        if len(anal_account_ids)==1:
            domain.append("('analytic_account_id','=',%d)"%anal_account_ids[0])
        elif len(anal_account_ids) > 1:
            domain.append("('analytic_account_id','in',["+','.join(map(str,anal_account_ids))+"])")
            
        domain = "[%s]"%','.join(map(str,domain))        
        
        
        result = {
            'domain': domain,
            'name': 'Selected Budget Lines',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'c2c_budget.line',
            'view_id': False,
            'type': 'ir.actions.act_window',
            'res_id':line_ids,
        }       
        
        return result
        
        
    states = {
    
        'init' : {
            'actions':[_build_form],
            'result' : {'type':'form', 'arch':arch, 'fields':_fields, 'state': [('end','Cancel'),('open','Show lines')]},
        },
        'open' : {
            'actions' : [],
            'result' : {'type':'action', 'action':_get_budget_lines, 'state':'end'},
        },

    }
    
    
wiz_advanced_search('budget.advanced_search')