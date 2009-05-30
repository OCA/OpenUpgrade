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


class compare_versions(StandardReport):  
    """this report display two budget versions side by side and compute the difference"""
    
    def get_template_title(self, cr, context):
        """ return the title of the report """
        
        return _("Versions Comparing")
    

    def get_story(self):
        """ return the report story """
        
        story = []


        version_obj = self.pool.get('c2c_budget.version')
        budget_item_obj = self.pool.get('c2c_budget.item')
        currency_obj = self.pool.get('res.currency')
     
        #
        # build the report tables
        #
        versions = version_obj.browse(self.cr, self.uid, [self.datas['form']['version_1'], self.datas['form']['version_2']])
        currency = currency_obj.browse(self.cr, self.uid, self.datas['form']['currency'])

        table = SimpleRowsTableBuilder(versions[0].budget_id.name+": "+versions[0].name+" "+self._('vs.')+" "+versions[1].name+" ["+currency.name+"]")
               
        #first column for structure
        table.add_text_column(self._('Structure'), 40*mm)
        table.add_num_column(versions[0].name)
        table.add_num_column(versions[1].name)
        table.add_num_column(versions[0].name+" - "+versions[1].name)
        
        
        #
        # gather datas
        # 
        
        v1_values = version_obj.get_budget_values(self.cr, self.uid, versions[0], self.objects, context=self.context)
        v2_values = version_obj.get_budget_values(self.cr, self.uid, versions[1], self.objects, context=self.context)

        #change from version currency to select currency
        change_v1_values = {}
        change_v2_values = {}        
        versions_diff = {}
        for id in v1_values:
            change_v1_values[id] = c2c_helper.exchange_currency(self.cr, v1_values[id], versions[0].currency_id.id, currency.id, time.strptime(versions[0].create_date, '%Y-%m-%d %H:%M:%S'))
            change_v2_values[id] = c2c_helper.exchange_currency(self.cr, v2_values[id], versions[1].currency_id.id, currency.id, time.strptime(versions[1].create_date, '%Y-%m-%d %H:%M:%S'))
            if change_v1_values[id] == 'error' or change_v2_values[id] == 'error':
                versions_diff[id] = 'error'
            else:
                versions_diff[id] = change_v1_values[id] - change_v2_values[id]
             
           
            
            
        #
        # add data to the table
        #
        items = budget_item_obj.get_sorted_list(self.cr, self.uid, versions[0].budget_id.budget_item_id.id)            
            
        for i in items:
                
            #do not add invisible items
            if i.style != 'invisible' :
                
                item_cell = ItemCell(i)
                table.add_custom_cell(item_cell)
                
                cell = BudgetNumCell(change_v1_values[i.id], 0)
                cell.copy_style(item_cell)
                table.add_custom_cell(cell)

                cell = BudgetNumCell(change_v2_values[i.id], 0)
                cell.copy_style(item_cell)
                table.add_custom_cell(cell)

                cell = BudgetNumCell(versions_diff[i.id], 0)
                cell.copy_style(item_cell)
                table.add_custom_cell(cell)

                                      
        story.append(table.get_table())         

        return story
    

           
compare_versions('report.compare_versions', "Versions Comparing", 'c2c_budget.line', StandardReport.A4_PORTRAIT)        
