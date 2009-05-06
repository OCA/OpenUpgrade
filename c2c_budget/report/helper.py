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

from c2c_reporting_tools.core.table_elements import *


class ItemCell(TextCellData):
    """ special cell for budget structure items. It's a text cell that handle a special style called "bold" """
    
    def __init__(self, item):
        """constructor"""
        super(ItemCell, self).__init__(item.name)
        
        if item.style == 'bold':
            self.font = "Helvetica-Bold"
            self.background_color = "#EEEEEE"


class PercentCell(NumCellData):
    """ special cell for % values. Basically, a NumCell with % next to the number """
    
    def get_raw_content(self, column_data, row_values, col_values):
        """ return the content of the cell without the surrounding Paragraph tags"""
        
        if self.value == 'error':
            return "-" 
        
        num = super(PercentCell, self).get_raw_content(column_data, row_values, col_values)
        return str(num)+" %"

        
class BudgetNumCell(NumCellData):
    """ special cell for budget values.  basically, a NumCell that display "Error!" in case the value is "error". """
    
    def _get_instant_value(self, column_data, row_values, col_values):
        """ return the numerical value of the cell or 0 in case the value is 'error' """
        
        if self.value == 'error':
            return 0
        return self.value
    
    def get_raw_content(self, column_data, row_values, col_values):
        """ return the formated value or 'Error!' in case the value is 'error' """
        if self.value == 'error':
            return "Formula Error!" 
        return super(BudgetNumCell, self).get_raw_content(column_data, row_values, col_values)
