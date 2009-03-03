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

from c2c_reporting_tools.reports.standard_report import *
from c2c_reporting_tools.flowables.simple_row_table import *
from c2c_reporting_tools.c2c_helper import *
from c2c_reporting_tools.translation import _
from reportlab.platypus import *
from c2c_budget.report.helper import *


class budget_vs_reality(StandardReport):  
    """this report compare a budget's version with its pending real values"""
    
    def get_template_title(self, cr, context):
        """ return the title of the report """
        return _("Budget Vs. Reality")
    

    def get_story(self):
        """ return the report story """
        
        story = []

        line_obj = self.pool.get('c2c_budget.line')
        version_obj = self.pool.get('c2c_budget.version')
        budget_item_obj = self.pool.get('c2c_budget.item')
        project_obj = self.pool.get('c2c_budget.report_abstraction').get_project_group_object(self.cr, self.uid, self.context)
  
     
        #do we split the tables by aa?
        aa_groups = []
        if (self.datas['form']['split_by_aa']):
            #group by selected AA 
            if len(self.datas['form']['analytic_accounts'][0][2]) > 0:
                aa_groups += project_obj.browse(self.cr, self.uid, self.datas['form']['analytic_accounts'][0][2], context=self.context)
            #group by each AA linked by one line
            else: 
                aa_groups += project_obj.browse(self.cr, self.uid, line_obj.get_projects(self.cr, self.uid, self.objects, self.context), context=self.context)
        else:
            aa_groups = [True] #true means no split by aa
     
     
     
        #
        # build the report tables
        #
        versions = version_obj.browse(self.cr, self.uid, self.datas['form']['version_ids'])
        
        for v in versions: 
            #a table per version/group
            for aa in aa_groups:
            
                title = ""
                #no split by AA
                if type(aa) == bool and aa:
                    title = v.budget_id.name+": "+v.name+" ["+v.currency_id.name+"]"
                    lines = self.objects
                #group by a AA
                else:
                    title = v.budget_id.name+": "+v.name+": "+aa.name+" ["+v.currency_id.name+"]"
                    lines = line_obj.filter_by_analytic_account(self.cr, self.uid, self.objects, [aa.id], context=self.context)
            
            
                table = SimpleRowsTableBuilder(title)
                   
                #first column for structure
                table.add_text_column(self._('Structure'), 40*mm)
                table.add_num_column(v.name)
                table.add_num_column(self._('Real'))
                table.add_num_column(v.name+" - "+self._('Real'))
                
                
                #
                # gather datas
                # 
                items = budget_item_obj.get_sorted_list(self.cr, self.uid, v.budget_id.budget_item_id.id)            
        
                
                budget_values = version_obj.get_budget_values(self.cr, self.uid, v, lines, context=self.context)
                
                #no split by AA
                if type(aa) == bool and aa:
                    #get real values from account move lines
                    real_values = version_obj.get_real_values(self.cr, self.uid, v, lines, context=self.context)
                    
                #group by a AA
                else:                
                    #get real values from analytic move lines
                    real_values = version_obj.get_real_values_from_analytic_accounts(self.cr, self.uid, v, lines, context=self.context)
        
                # compute the balance
                balance = {}
                for id in budget_values:
                    if budget_values[id] == 'error' or real_values[id] == 'error':
                        balance[id] = 'error'
                    else:
                        balance[id] = budget_values[id] - real_values[id]
                     
                   
                #
                # add data to the table
                #            
                for i in items:
                        
                    #do not add invisible items
                    if i.style != 'invisible' :
                        
                        item_cell = ItemCell(i)
                        table.add_custom_cell(item_cell)
                        
                        cell = BudgetNumCell(budget_values[i.id], 0)
                        cell.copy_style(item_cell)
                        table.add_custom_cell(cell)
        
                        cell = BudgetNumCell(real_values[i.id], 0)
                        cell.copy_style(item_cell)
                        table.add_custom_cell(cell)
        
                        cell = BudgetNumCell(balance[i.id], 0)
                        cell.copy_style(item_cell)
                        table.add_custom_cell(cell)
                                              
                story.append(table.get_table())         
                story.append(PageBreak())
            
        return story
    

           
budget_vs_reality('report.budget_vs_reality', "Budget Vs. Reality", 'c2c_budget.line', StandardReport.A4_PORTRAIT)        
