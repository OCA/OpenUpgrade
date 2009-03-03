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
#    - SimpleRowsTableBuilder. a factory to create simple row tables
#                                - a title
#                                - a line of headers
#                                - then X rows of values
#    
#
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
from reportlab import platypus
from reportlab.platypus import *
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib import colors
from c2c_reporting_tools.core.table_elements import *
                    
    

class SimpleRowsTableBuilder(object):
    """ Tool to generate a table that can be insert in reports.
        With this object, you can create simple tables: - a title
                                                        - a line of headers
                                                        - X rows of datas
        usage: - create a an object of this class.
                - first call add_*_column() methods to define table columns from left to right
                - then add add_*_cell() methods to fill the table with data. Cells are added side by side on a row and pass to the next row when current row is full
                - finally, call get_table() to get the flowable object to pass to the template
    """
    
    
    DEFAULT_FONT = "Helvetica"
    DEFAULT_FONT_SIZE = 8    
    HEADER_FONT = 'Helvetica-Oblique'
    
    REPEAT_ROWS = 2        
            
    data = None
    forced_width = None
    
    
    def __init__(self, title=""):
        """ constructor
            title = table title
        """            
        self.data = SimpleRowsTableData(title)
        
    def set_title(self, title):
        """ redefine the title passed in the construtor """
        self.data.title = title


    def add_column(self, title, width='auto'):
        """ add a standard column to the table 
            title = column title
        """
        self.data._add_column(ColumnData(title, width))

    def add_custom_column(self, columnObject):
        """ add a custom column created by extending /core/table_elements.py/ColData
        """
        self.data._add_column(columnObject)

    
    def add_text_column(self, title, width='auto', truncate_length=None, indent=None):
        """ add a text column to the table 
            title = column title
            truncate_length = text max length
            indent = text indentation
        """
        self.data._add_column(TextColData(title, width, truncate_length, indent))

    
    def add_num_column(self, title, width='auto', decimals=2, separator="'"):
        """ add a numerical column to the table
            title = column tite
            decimal= number of digits after the comma
            separator = thousands separator
        """
        self.data._add_column(NumColData(title, width, decimals, separator))


    def add_money_column(self, title, width='auto', currency=None, decimals=2, separator="'"):
        """ add a monetary column to the table
            title = the column title
            currency =  3 char currency text
            decimal = number of digits 
            separator= thousands separator char
        """
        self.data._add_column(MoneyColData(title, width, currency, separator))   

       
    def add_date_column(self, title, width='auto', format="%d.%m.%Y"):
        """ add a date column to the table
            title = the column title
            format = the date format
        """
        self.data._add_column(DateColData(title, width, format))

    
    def add_nested_columns(self, tableBuilder, width='auto'):
        """ add nested column(s) to a table. Nested columns are columns that contain multiple rows of data for each main row.
            - Using one nested column allow to create a column that contain lists of values for each rows. 
            - Using more that one nested columns allow to have matching lists that stay aligned whatever they contain on each row
            pass to this method another SimpleRowsTableBuilder object that contain only columns definitions and no data
            Here is an exemple:
            
                table_data = SimpleRowsTableBuilder(title)
                table_data.add_text_column(_('User'), "35%")
                
                nested_table = SimpleRowsTableBuilder()
                nested_table.add_text_column(_('Projects'))
                nested_table.add_num_column(_('Time'))        
                
                table_data.add_nested_columns(nested_table, "65%")
            
        """
        self.data._add_column(NestedTableColData(tableBuilder, width))
    

    def add_cell(self, value):
        """ add a default cell """
        self.data._add_cell(CellData(value))
                             
    def add_empty_cell(self):
        """ add an empty cell to the table """
        self.data._add_cell(CellData(''))
    
    
    def add_text_cell(self, value, truncate_length=None, indent=None):
        """ add a cell that contain text value 
            value = the cell content
            truncate_length = the text max length
            indent = text indentation
        """
        self.data._add_cell(TextCellData(value, truncate_length, indent))

    
    def add_num_cell(self, value, decimals=2, separator="'"):
        """ add a cell that contain numerical value 
            value = the cell content
            decimals= number of digits
            separator = thousand separator char
        """
        self.data._add_cell(NumCellData(value, decimals, separator))


    def add_money_cell(self, value, currency=None, decimals=2, separator="'"):
        """ add a cell that contain monetary value
            value = the cell content
            currency = 3 char currency
            decimals = number of digits
            separator = thousand separator
        """
        self.data._add_cell(MoneyCellData(value, currency, decimals, separator))


    def add_date_cell(self, value, format=None):
        """add a cell that contain date value
           value = the date (time struct)
           format = date format
        """
        self.data._add_cell(DateCellData(value, format))
                
                
    def add_nested_cells(self, tableBuilder):
        """ add a cell that contain lists of values. See add_nested_columns() for details. 
            pass to this method a SimpleRowsTableBuilder object that contain column definitions and values for this row.
            Here is an exemple:     
            
                table_data.add_text_cell(user_datas.user_obj.name)

                nested_values = copy.deepcopy(nested_table)
                for project in project_infos:
                    nested_values.add_text_cell(project.name)
                    nested_values.add_num_cell(project.time)
                    
                table_data.add_nested_cells(nested_values)
        """
        self.data._add_cell(NestedTableCellData(tableBuilder))


    def add_subtotal_num_cell(self, decimal=2, separator="'"):
        """ add a cell that will display the total of above cells (display is bold)"""
        self.data._add_cell(SubtotalNumCellData(decimal, separator))        
        
        
    def add_subtotal_money_cell(self, currency="", decimal=2, separator="'"):
        """ add a cell that will display the total of above cells  as a money value (with a currency) (display is bold) """
        self.data._add_cell(SubtotalMoneyCellData(currency, decimal, separator))
        
        
        
    def add_custom_cell(self, cellObject):
        """ add a custom cell created by extending /core/table_elements.py/CellData """
        self.data._add_cell(cellObject)
        
    def add_custom_column(self, colObject):
        """ add a custom column created by extending /core/table_elements.py/CellData """
        self.data._add_column(colObject)
        
        
        
    def add_row(self, row_values):
        """ add a row of values. Can replace multiple calls to add_*_cell() by using default values for each columns 
            row_values is a list of values to insert in table
        """
    
        #for each column, find its type and add the right cell
        cpt = 0
        for col in self.data.columns: 
            if cpt+1 <= len(row_values):
                value = row_values[cpt]
            else: 
                value = None
            
            self.data._add_cell(col.accepted_cell(value))
            cpt += 1
            
    
    def add_rows(self, rows_values):
        """ add multiple rows. Can replace multiple calls to add_row() 
            row_values is a list of rows. rows are lists of values to insert in table
        """
        
        for row in rows_values:
            self.add_row(row)
            
            
    def set_width(self, width):
        """ allow to force the width of columns and overwrite the width defined in add_*_columns() methods """
        self.forced_width = width


    def get_table(self):
        """
            return the flowable object that can be insert into a template to build the rapport.
            call this method after having filled the object with add_*_column() and add_*_cell() methods
            - 'width' can be either the whole table width or a list of column width, absolute or percents. for exemple ('10%','10%','80%') or (200, 200, 600) or 1000         
        """

        table = self._build_table()
    
        column_width = self._get_columns_width()             
        table = SimpleRowsTable(table, column_width, repeatRows=self.REPEAT_ROWS)
        
        styles = self._get_styles()
        table.setStyle(TableStyle(styles))
        return table






    def _get_standard_styles(self):
        """ return the standard styles to apply to the whole table """
        
        #common styles for the table
        return [
                  #global font for the whole graphic
                  ('FONT', (0,0), (-1,-1),self.DEFAULT_FONT, self.DEFAULT_FONT_SIZE),
                  #top align
                  ('VALIGN', (0,0), (-1,-1), 'TOP'),
                ]
    
        
    def _get_title_style(self):
        """ return styles that are related to the title """
        
        return [  #title border
                  ('BOX', (0,0), (-1,0), 1, colors.black),
                  #title background
                  ('BACKGROUND', (0,0), (-1,0), '#cccccc'),
                  # main frame arround the whole table
                  ('BOX', (0,0), (-1,-1), 1, colors.black),
                  # black line below the headers           
                  ('LINEBELOW', (0, 1), (-1, 1), 1, colors.black), 
                  
               ]


    def _get_title_row(self):
        """ called to build the whole table. Return the first row (the one that contain the title) """
        return [self.data.title] + (len(self.data.columns) -1) * ['']
        
    
    
    def _get_headers_styles(self, Y_offset=1):        
        """ return the table styles to apply. A list of tuples to pass to TableStyle's constructor
            It define style for each columns'header
        """
        
        #header in oblique
        styles = [('FONTNAME', (0,Y_offset), (-1,Y_offset) , self.HEADER_FONT)]
        
        #define styles for each column
        cpt = 0     
        for column in self.data.columns:            
            
                          
            #handle alignment style  
            if column.align != None:    
                styles.append( ('ALIGN', (cpt, Y_offset), (cpt, Y_offset), column.align) )
            # lignt grey columns separators            
            styles.append( ('LINEAFTER', (cpt, Y_offset), (cpt, Y_offset), 0.1, colors.grey) ) 
            
            #handle special styles for headers
            special_styles = column.get_header_special_style()
            for style in special_styles:
                
                #add coorinates to the styles returned by get_special_style
                special_style = (style[0], (cpt, Y_offset), (cpt, Y_offset))
                special_style += style[1:]
                styles.append(special_style)
                
            cpt+=1
        return styles
            
            
    def _get_header_row(self):
        """ called to build the whole table. Return the second row (the one that contain the headers) """

        #the second line contain headers
        header = []
                
        for column in self.data.columns:            
            #add the title
            header.append(column.get_title())
        return header
            
            
    def _get_data_styles(self, Y_offset=2):
        """ return the table styles to apply. A list of tuples to pass to TableStyle's constructor
            It define style for each columns'data
        """

        styles = []

        #define styles for each column
        cpt = 0     
        for column in self.data.columns:            
                          
            #handle alignment style 
            if column.align != None:
                styles.append(('ALIGN', (cpt, Y_offset), (cpt, -1), column.align))
            # lignt grey columns separators
            styles.append(('LINEAFTER', (cpt, Y_offset), (cpt, -1), 0.1, colors.grey))
            #lignt grey lines separator
            styles.append(('INNERGRID', (cpt, Y_offset), (cpt, -1), 0.1, colors.grey))

            
            #handle special styles for content
            special_styles = column.get_content_special_style()
            for style in special_styles:
                #add coorinates to the styles returned by get_special_style
                special_style = (style[0], (cpt, Y_offset), (cpt, -1))
                special_style += style[1:]
                styles.append(special_style)
            
            cpt+= 1

        #go through all cells to get special style        
        cptY = Y_offset
        for row in self.data.table:
            cptX = 0
            for cell in row: 
                cell_styles = cell.get_style(self.data.columns[cptX])
                for style in cell_styles:
                    #add coorinates to the styles returned by get_style
                    cell_style = (style[0], (cptX, cptY), (cptX, cptY))
                    cell_style += style[1:]
                    styles.append(cell_style)
                cptX += 1
            cptY += 1

        return styles

        
    def _get_data_rows(self):
        """ called to build the whole table. Return all data rows (those that comes after the header) """
        table = []
        
        #init the table that will contain all tables ordered by columns
        colsValues = []
        for column in self.data.columns:
            colsValues.append([])
        
        for rowValues in self.data.get_table():
            row = []
            cpt = 0
            for cellData in rowValues:
                colsValues[cpt].append(cellData)
                #ask for content of the cell and give it the row and column values (in case the cell is a total cell for instance)
                row.append(cellData.get_content(self.data.columns[cpt], rowValues, colsValues[cpt]))
                cpt += 1
            table.append(row)
        
        return table
        
    def _get_styles(self):
        """ return the table styles to apply. A list of tuples to pass to TableStyle's constructor
            It define style for the whole table and default styles for each columns (headers and datas)
        """
        
        styles = []
        
        styles += self._get_standard_styles()
        styles += self._get_title_style()
        styles += self._get_headers_styles()
        styles += self._get_data_styles(Y_offset=self.REPEAT_ROWS)

        return styles
     
        
    def _build_table(self):
        """ build the table. Build each row and columns add all text in it """
        
        table = []

        #first line for the planning name
        table.append(self._get_title_row())
        #headers
        table.append(self._get_header_row())        
        # cells
        table = table + self._get_data_rows()       
        
        return table
        
        
    def _get_columns_width(self):
        """ return the list of each column width. """
        
        #width has been defined with set_width()
        if self.forced_width != None:

            widths = list(self.forced_width)
            #if there is missing columns, complete with default width
            while len(widths) < len(self.data.columns):
                widths.append('*')
            while len(widths) > len(self.data.columns):
                widths.pop()
                    
        #width has been defined through all columns data
        else: 
            
            #count the number of 'auto' columns and compute the total of widths in percent
            auto_cols = 0
            tot_percent = 0
            for c in self.data.columns:
                if c._width == 'auto':
                    auto_cols += 1
                elif "%" in str(c._width):
                    width = c._width
                    tot_percent += int(width.replace('%', ''))
        
            #have to find the width of autowidth cols
            auto_col_width = 0
            if auto_cols > 0:
                
                if tot_percent < 100:
                    remaining_percent = 100 - tot_percent
                    auto_col_width = str(remaining_percent/ float(auto_cols))+"%" 
                #width in percent are bigger than 100%, simply define a fixed width...
                else:
                    auto_col_width = "50"
            
            # build the list of widths
            widths = []
            for c in self.data.columns:
                if c._width == 'auto':
                    widths.append(auto_col_width)
                else: 
                    widths.append(c._width)
            
        return widths
    
                            
        
class SimpleRowsTableData(object):
    """ this object is use internally by SimpleRowsTableBuilder to define the table structure and content """
    title = ""
    
    # a list of columns. Columns are ColData objects    
    columns = []       
    
    # a list of rows. Rows are lists too and contain CellData
    table = []
    current_row = []
    
    table_empty= True
    
    def __init__(self, title=""):
        """ constructor 
            title = table title """
        self.title = title
        self.columns = []
        self.table = []
        self.current_row = []
        self.table_empty= True
    

    def _add_column(self, column):
        ''' define a new column in the table'''
        if self.table_empty:
            self.columns.append(column)
        else: 
            raise Exception('Table already contain cells, you can not add columns anymore once you started to add cells.')


    def _add_cell(self, cell):
        ''' add a cell in the next position in the table '''
                       
        if (not self.columns):
            raise Exception('No column defined, add columns first, then cells')
        
        self.current_row.append(cell)

        #if the current_row is full, store the row in the table and create a new one
        if len(self.current_row) == len(self.columns):
            self.table.append(self.current_row)
            self.current_row = []
            
        
        self.table_empty = False
        
        
    def get_table(self):
        """ complete the table with empty cells if the last row is not complete and return it """
        #complete the last row with empty cells
        while self.current_row != []:
            self._add_cell(CellData(""))
        
        return self.table
 
        
class SimpleRowsTable(Table):
    """ the flowable object returned by SimpleRowsTableBuilder->get_table() """
    
    def draw(self):
        """ called by the template engine to ask the table to draw itself """
        
        #on each page, close the bottom table border
        self.setStyle(TableStyle([
                                  #line that separate the items and the datas
                                  ('LINEBELOW', (0, -1), (-1, -1), 1, colors.black),                                  
                                ]))
        
        #super call "old style"
        Table.draw(self)

           
class C2cStyleRowsTable(SimpleRowsTableBuilder):
    """ Over load style function to set a new style for this report """
    def _get_title_style(self):
        """ return styles that are related to the title """
        
        return [  #title border
                  ('BOX', (0,0), (-1,0), 1, colors.white),
                  #title background
                  ('BACKGROUND', (0,0), (-1,0), colors.white),
                  # main frame arround the whole table
                  ('BOX', (0,0), (-1,-1), 1, colors.black),
                  # black line below the headers           
                  ('LINEBELOW', (0, 0), (-1, -1), 1, '#e6e6e6'), 
                  
               ]
    