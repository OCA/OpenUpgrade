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
    <form string="Budget by periods" height="200" width="800">
        <field name="compare_item" />
        <newline/>
        <field name="periods_nbr" />
        <field name="from_date" />
        <newline/>
        <field name="display_previous" />
        <field name="display_next" /> 
    """
        
_form_footer = """
    </form>"""


_fields = {
    'compare_item': {'string':'Ref. For % Comparing: ', 'type':'many2one', 'relation':'c2c_budget.item'},
    'from_date': {'string':'Starting From:', 'type':'date', 'required':True },
    'periods_nbr': {'string':'Nb Periods', 'type':'selection', 'selection':[(i,i) for i in range(0, 13)], 'default':lambda *a: 12},
    'display_previous': {'string':'Display Previous', 'type':'boolean', 'default':lambda *a:True},
    'display_next': {'string':'Display Next', 'type':'boolean', 'default':lambda *a:True},
}





class wiz_budget_by_period(wizard.interface):
    """ this wizard display options to print the budget by periods report """


    def _build_form(self, cr, uid, data, context):
        """complete the form with abstracted parts from  c2c_budget.wizard_abstraction """
        
        wiz_abstract_obj = pooler.get_pool(cr.dbname).get('c2c_budget.wizard_abstraction')
        
        #complete the form with the abstraction
        arch.string = _form_header + wiz_abstract_obj.budget_by_period_get_form(cr, uid, data,context) + _form_footer
        
        #complete the fields with the abstraction
        fields = wiz_abstract_obj.budget_by_period_get_fields(cr, uid, data,context)
        for f in fields:
            _fields[f] = fields[f]
        
        
        return {} 


    def _init_fields(self, cr, uid, data, context={}):
        """ init the form's fields """

        budget_obj = pooler.get_pool(cr.dbname).get('c2c_budget')
        
        res = {}

        #we come from budget
        if data['model'] == 'c2c_budget':
            
            #from_date must match budget's start_date
            budgets = budget_obj.browse(cr, uid, data['ids'], context=context)
            res['from_date'] = None
            for b in budgets:
                if res['from_date'] is None or res['from_date'] > b.start_date:
                    res['from_date'] = b.start_date

        #we come from versions
        elif data['model'] == 'c2c_budget.version':
            
            #from_date must match budget's start_date
            version_obj = pooler.get_pool(cr.dbname).get('c2c_budget.version')            
            budgets_ids = [v.budget_id.id for v in version_obj.browse(cr, uid, data['ids'], context)]
            budgets = budget_obj.browse(cr, uid, budgets_ids, context=context)
            res['from_date'] = None
            for b in budgets:
                if res['from_date'] is None or res['from_date'] > b.start_date:
                    res['from_date'] = b.start_date
            
        #we come from lines
        else:
            
            #from_date must match lines' first period
            line_obj = pooler.get_pool(cr.dbname).get('c2c_budget.line')
            lines = line_obj.browse(cr, uid, data['ids'])
            
            
            from_date = None
            for l in lines: 
                try:
                    if (from_date is None) or (from_date > l.period_id.date_start):
                        from_date = l.period_id.date_start
                #if there is an access rules error, just ignore it and continue
                except Exception, e: 
                    pass
            
            if from_date is not None:
                res['from_date'] = from_date
                
        return res   

    
    def _get_budget_lines(self, cr, uid, data, context):
        """ retrieve lines to work on. This is done to limit the amount of data to treat in the report"""
        
        line_obj = pooler.get_pool(cr.dbname).get('c2c_budget.line')
        period_obj = pooler.get_pool(cr.dbname).get('account.period')
        version_obj = pooler.get_pool(cr.dbname).get('c2c_budget.version')
        
        #
        # retrive budget lines to work on
        #
        
        #we come from budget
        if data['model'] == 'c2c_budget':
            budget_obj = pooler.get_pool(cr.dbname).get('c2c_budget')
            budgets = budget_obj.browse(cr, uid, data['ids'])
            lines = []
            for b in budgets:
                for v in b.budget_version_ids:
                    for l in v.budget_line_ids:
                        lines.append(l)
        
        
        #we come from versions
        elif data['model'] == 'c2c_budget.version':
            versions = version_obj.browse(cr, uid, data['ids'])
            lines = []
            for v in versions:
                for l in v.budget_line_ids:
                    lines.append(l)
              
                    
        #we come from lines
        else:
            lines = line_obj.browse(cr, uid, data['ids'])
        
            
        #define calculation start period
        date_start = None
        if not data['form']['display_previous']:
            date_start = data['form']['from_date']
            
        #define calculation end_period
        date_end = None
        if not data['form']['display_next']:
                #find all versions concerned by the lines
                versions = line_obj.get_versions(cr, uid, lines, context)
                for v in versions:                     
                    start_period = version_obj.get_period(cr, uid, v, data['form']['from_date'], context)
                    
                    #for each version find its periods
                    periods = v.get_next_periods(cr, uid, v, start_period, data['form']['periods_nbr'], context)
                    if len(periods) > 0:
                        end_period = periods[-1]
                        #amongst all version's period, find the latest
                        if date_end is None or date_end < end_period.date_stop:
                            date_end = end_period.date_stop
            
        #limit the amount of lines to work onby filtering by date
        lines = line_obj.filter_by_date(cr, uid, lines, date_start=date_start, date_end=date_end)


        # limit lines to selected analytic accounts
        if len(data['form']['analytic_accounts'][0][2]) > 0:
            account_ids = data['form']['analytic_accounts'][0][2]
            lines = line_obj.filter_by_analytic_account(cr, uid, lines, account_ids)
        
        if len(lines) == 0:
            raise wizard.except_wizard('No data', "There is no budget lines to work on, please make another selection")
            
        
        values = {'ids': [l.id for l in lines]
                  }    
        
        return values
        
        
    states = {
    
        'init' : {
            'actions':[_build_form, _init_fields],
            'result' : {'type':'form', 'arch':arch, 'fields':_fields, 'state': [('end','Cancel'),('print','Print')]},
        },
        'print' : {
            'actions' : [_get_budget_lines],
            'result' : {'type':'print', 'report':'budget_by_period', 'get_id_from_action':True, 'state':'end'},
        },

    }
    
    
wiz_budget_by_period('budget.by.periods')