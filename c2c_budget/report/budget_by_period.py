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

class budget_by_period(StandardReport):  
    """ Report that display a budget. It can be split by period and compare to an item (in %) """
    
    def get_template_title(self, cr, context):
        """ return the title of the report """
        return _("Budget by Periods")
    

    def get_story(self):
        """ build the report """
        
        cr=  self.cr 
        context= self.context
        
        """ return the report story """
        story = []

        budget_item_obj = self.pool.get('c2c_budget.item')
        #period_obj = self.pool.get('account.period')
        line_obj = self.pool.get('c2c_budget.line')
        version_obj = self.pool.get('c2c_budget.version')
        project_obj = self.pool.get('c2c_budget.report_abstraction').get_project_group_object(self.cr, self.uid, self.context)
        
        
        display_previous = self.datas['form']['display_previous']
        display_next     = self.datas['form']['display_next']
        reference_item = None
        if self.datas['form']['compare_item']:
            reference_item   = budget_item_obj.browse(self.cr, self.uid, self.datas['form']['compare_item'], context=self.context)
        
        
        #a table per version
        versions = line_obj.get_versions(self.cr, self.uid, self.objects, context=self.context)        
        for version in versions:
        
        
            periods = []
            if self.datas['form']['periods_nbr'] >= 1:
                start_period = version_obj.get_period(self.cr, self.uid, version, self.datas['form']['from_date'], context=self.context)
                periods.append(start_period)
                if self.datas['form']['periods_nbr'] >= 2:
                    next_periods = version_obj.get_next_periods(self.cr, self.uid, version, start_period, self.datas['form']['periods_nbr']-1, context=self.context)
                    periods = periods + next_periods
            analytic_accounts = []
            

            #
            #build a list of columns we are going to display. the list contain dictionnaries of informations about the column:
            #
            columns = []
            
            if display_previous and len(periods) > 0:
                #get the period before the first one
                to_period = version_obj.get_previous_period(self.cr, self.uid, version, periods[0], self.context)
                if to_period is not None:
                    info = {'from': None, 
                            'to': to_period,
                            'title': self._('Previous')}
                    columns.append(info)
                
            for period in periods:
                #construct the period title
                text_header = period.name
                if period.name == None:
                    text_header = period.code
            
                parts = text_header.split(" ")
                text_header = c2c_helper.ellipsis(parts[0], 10, '.')
                
                info = {'from': period,
                        'to': period,
                        'title': period.name
                        }
                columns.append(info)
    
            if display_next and len(periods) > 0:
                #get the period after the last one
                from_period = version_obj.get_next_period(self.cr, self.uid, version, periods[-1], self.context)
                if from_period is not None:
                    info = {'from': from_period, 
                            'to': None,
                            'title': self._('Next')}
                    columns.append(info)
    
            #total column
            info = {'from': None,
                    'to': None,
                    'title': self._('Total'),
                    'isTotal': True}
            
    
            columns.append(info)
    
    
            #
            # build the report tables
            #
            
            #do we split the tables by aa?
            aa_groups = []
            if (self.datas['form']['split_by_aa']):
                #group by selected AA 
                if len(self.datas['form']['analytic_accounts'][0][2]) > 0:
                    aa_groups +=  project_obj.browse(self.cr, self.uid, self.datas['form']['analytic_accounts'][0][2], context=self.context)
                #group by each AA linked by one line
                else: 
                    aa_groups += project_obj.browse(self.cr, self.uid, line_obj.get_projects(self.cr, self.uid, self.objects, self.context), context=self.context)
            else:
                aa_groups = [True] #true means no split by aa
            
            
            #a table per version/group
            for aa in aa_groups:
                
                title = ""
                #no split by AA
                if type(aa) == bool and aa:
                    title = version.budget_id.name+": "+version.name+" ["+version.currency_id.name+"]"
                    lines = self.objects
                #group by a AA
                else:
                    title = version.budget_id.name+": "+version.name+": "+aa.name+" ["+version.currency_id.name+"]"
                    lines = line_obj.filter_by_analytic_account(self.cr, self.uid, self.objects, [aa.id], context=self.context)
                    
                table = SimpleRowsTableBuilder(title)
                   
                #first column for structure
                table.add_text_column(self._('Structure'), 40*mm)
             
                #reduce the font size if there is lot of columns
                header_font_size = 8
                font_size = 8
                if len(columns) > 12:
                    header_font_size = 6
                    font_size = 6
                    
                #build table columns
                for column in columns:           
                    #last Column Total in bold
                    if 'isTotal' in column:
                        col = MoneyColData(info['title'], 30*mm)
                        col.header_font = "Helvetica-BoldOblique"
                        table.add_custom_column(col)                    
                    #normal columns
                    else:
                        col = NumColData(column['title'])
                        col.header_font_size = header_font_size
                        col.font_size = font_size
                        table.add_custom_column(col)
                        
                # % column
                if reference_item is not None:
                        col = NumColData(self._('%')+" "+reference_item.code, 15*mm)
                        col.align = 'RIGHT'
                        col.header_font_size = header_font_size
                        col.font_size = font_size
                        table.add_custom_column(col)
                
                    
                #            
                #gather data
                #
                
                columns_data = []
                for column in columns:
                    columns_data.append(version_obj.get_filtered_budget_values(self.cr, self.uid, version, lines, column['from'], column['to'], self.context))
                
                reference_data = []
                if reference_item is not None:
                    reference_data = version_obj.get_percent_values(self.cr, self.uid, columns_data[-1], reference_item.id)
                
                
                
                #
                # add data to the table
                #
                items = budget_item_obj.get_sorted_list(self.cr, self.uid, version.budget_id.budget_item_id.id)            
                
                for i in items:
                    
                    #do not add invisible items
                    if i.style != 'invisible' :
                        
                        item_cell = ItemCell(i)
                        table.add_custom_cell(item_cell)
                       
                        for column_data in columns_data:
                            cell = BudgetNumCell(column_data[i.id], 0)
                            cell.copy_style(item_cell)
                            table.add_custom_cell(cell)
                        
                        if reference_item is not None:
                            percent_cell = PercentCell(reference_data[i.id],1)
                            percent_cell.copy_style(item_cell)
                            table.add_custom_cell(percent_cell)
                   
                story.append(table.get_table())         
                story.append(PageBreak())

        return story
    

           
budget_by_period('report.budget_by_period', "Budget by Periods", 'c2c_budget.line', StandardReport.A4_LANDSCAPE)        
