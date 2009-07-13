# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) Camptocamp SA
# Author: Arnaud Wüst
#
#
#    This file is part of the c2c_report_tools module.
#    It contains the following class:
#
#    - KeyValueTableBuilder. a factory to create simple table that display pairs of key and values:
#                                - N keys, N values, displayed in 1 or more columns
#    
#
#
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
#from reportlab import platypus
#from reportlab.platypus import *
#from reportlab.lib.styles import ParagraphStyle
#from reportlab.lib import colors
from c2c_reporting_tools.flowables.simple_row_table import *
from c2c_reporting_tools.core.table_elements import *
#                    
#    

class KeyValueTableBuilder(SimpleRowsTableBuilder):
    """ Tool to generate a table that can be insert in reports.
        With this object, you can create simple tables that contain pairs of key and values, displayed on single or multiple columns
        
        usage: - create a an object of this class.
                - call add_key_column() or add_value_column() methods to define with columns contain Keys and which contain values
                - call add_key_cell  or add_*_cell() methods to define keys and values from left to right
                - finally, call get_table() to get the flowable object to pass to the template
    """
    
    REPEAT_ROWS = 1

        
                            
    def add_key_column(self, width='auto'):
        """ add a standard column to the table 
            title = column title
        """
        self.data._add_column(HeaderColData('', width))
        
                            
    def add_value_column(self, width='auto'):
        """ add a standard column to the table 
            title = column title
        """
        self.data._add_column(ColData('', width))      
                            
                       
    def add_key_cell(self, value):
        """ add a cell in a header column"""
        self.data._add_cell(HeaderCellData(value))     
                                           
        
        
    def _get_title_style(self):
        """ return styles that are related to the title """
        
        return [  #title border
                  ('BOX', (0,0), (-1,0), 1, colors.black),
                  #title background
                  ('BACKGROUND', (0,0), (-1,0), '#cccccc'),
                  # main frame arround the whole table
                  ('BOX', (0,0), (-1,-1), 1, colors.black),
                  
               ]
        
        
    def _get_styles(self):
        """ return the table styles to apply. A list of tuples to pass to TableStyle's constructor
            It define style for the whole table and default styles for each columns (headers and datas)
        """
        
        styles = []
        
        styles += self._get_standard_styles()
        styles += self._get_title_style()
        styles += self._get_data_styles(Y_offset=self.REPEAT_ROWS)
        return styles
     
        
    def _build_table(self):
        """ build the table. Build each row and columns add all text in it """
        
        table = []

        #first line for the planning name
        table.append(self._get_title_row())
        # cells
        table = table + self._get_data_rows()       
        
        return table

   
 
