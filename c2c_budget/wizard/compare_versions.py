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


class wiz_compare_versions(wizard.interface):
    """ display options to print the report that compare two versions """

    def _init_fields(self, cr, uid, data, context):
        """ init the form's fields """

        budget_obj = pooler.get_pool(cr.dbname).get('c2c_budget')
        
        res = {}

        #we come from budget
        if data['model'] == 'c2c_budget':
            budget_obj = pooler.get_pool(cr.dbname).get('c2c_budget')
            
            #init version and version 2 with the 2 first versions
            if len(data['ids']) >= 1:
                budget = budget_obj.browse(cr, uid, data['ids'][0])
                if len(budget.budget_version_ids) >= 1:
                    res['version_1'] = budget.budget_version_ids[0].id
                    res['currency'] = budget.budget_version_ids[0].currency_id.id
                if len(budget.budget_version_ids) >= 2:
                    res['version_2'] = budget.budget_version_ids[1].id
                

        #we come from versions
        elif data['model'] == 'c2c_budget.version':
            version_obj = pooler.get_pool(cr.dbname).get('c2c_budget.version')            

            #init version and version 2 with the 2 first versions
            if len(data['ids']) >= 1:
                res['version_1'] = data['ids'][0]
                res['currency'] = version_obj.browse(cr, uid, data['ids'][0], context=context).currency_id.id
            if len(data['ids']) >= 2:
                res['version_2'] = data['ids'][1]
            
            
        return res   

    
    def _get_budget_lines(self, cr, uid, data, context):
        """ retrieve lines to work on """
        
        #checkthe two versions belongs to the same budget
        version_obj = pooler.get_pool(cr.dbname).get('c2c_budget.version')            
        versions = version_obj.browse(cr, uid, [data['form']['version_1'], data['form']['version_2']], context=context)
        if versions[0].budget_id.id != versions[1].budget_id.id:
            raise wizard.except_wizard('Incompatible Versions', "The two selected versions do not belong to the same budget. Select two versions of the same budget to run the report")
            
        #find lines to work on
        line_obj = pooler.get_pool(cr.dbname).get('c2c_budget.line')
        period_obj = pooler.get_pool(cr.dbname).get('account.period')
        
        criteria = [('budget_version_id', 'in', [data['form']['version_1'], data['form']['version_2']])]
        if len(data['form']['periods'][0][2]) > 0:
            criteria.append(('period_id', 'in', data['form']['periods'][0][2]))
        
        line_ids = line_obj.search(cr, uid, criteria, context=context)
        
        values = {'ids': line_ids
                  }    
        
        return values
        
    _form = """<?xml version="1.0"?>
    <form string="Versions Comparing" width="800">
        
        <field name="version_1" />
        <field name="version_2" />
        <newline/>
        <field name="currency" />
        <newline/>

        <separator string="Select periods (empty for all)" colspan="4"/>
        <field name="periods" colspan="4"  nolabel="1" height="200" />
    </form>"""

    _fields = {
        'version_1': {'string':'Version 1', 'type':'many2one', 'relation':'c2c_budget.version', 'required':True },
        'version_2': {'string':'Version 2', 'type':'many2one', 'relation':'c2c_budget.version', 'required':True },
        'currency':  {'string':'Currency' , 'type':'many2one', 'relation':'res.currency', 'required':True },
        'periods':   {'string':'Periods'  , 'type':'many2many','relation':'account.period'}, 
    }
        
    states = {
    
        'init' : {
            'actions':[_init_fields],
            'result' : {'type':'form', 'arch':_form, 'fields':_fields, 'state': [('end','Cancel'),('print','Print')]},
        },
        'print' : {
            'actions' : [_get_budget_lines],
            'result' : {'type':'print', 'report':'compare_versions', 'get_id_from_action':True, 'state':'end'},
        },

    }
    
    
wiz_compare_versions('compare.budget.versions')