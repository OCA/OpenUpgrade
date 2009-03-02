# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) Camptocamp SA - http://www.camptocamp.com
# Author: Arnaud Wüst
#
#
#    This file is part of the c2c_report_tools module.
#    It contains classes internaly used by tables components
#
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsability of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking fo.r a ready-to-use solution with commercial
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

import time
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import *
from c2c_reporting_tools.c2c_helper import *
from reportlab.lib.units import mm
from reportlab.lib import colors
import reportlab.lib.enums

class CellData(object):
    """ a cell of the table 
        do not use it directly, call SimpleRowsTableData.add_cell() instead        
    """

    default_align = 'LEFT' #alignment use if the column alignment is missing
    value = None   
    _pos = None
    
    align= None # use this to override the col alignment. none means "inherit"
    font = None  # inherited from col
    font_size = None # inherit from col
    background_color = None #no color
    
    def __init__(self, value):
        """ constructor 
            value = cell's content """
        self.value = value
        self._pos = None
        
    def copy_style(self, cellData, exceptions=['align']):
        """ helper to copy style from another cell """
        
        if 'align' not in exceptions: 
            self.align = cellData.align
        if 'font' not in exceptions:
            self.font = cellData.font
        if 'font_size' not in exceptions:
            self.font_size = cellData.font_size
        if 'background_color' not in exceptions:
            self.background_color = cellData.background_color
        
        
        
    def get_content(self, column_data, row_values, col_values):
        """ return the content of the cell 
            column_data is a *ColData object that define the column
            row_values is a list of CellData of the whole row where the cell has to be placed
            col_values is a list of CellData THAT ARE ABOVE this cell in the table
        """
        
        if self.value == None: 
            return ""
        
        return self.value


    def get_align_code(self, column_data):
        """return the reportlab code corresponding to the alignment """
        
        align= self.get_alignment(column_data)
        if (align == 'CENTER'):
            res = reportlab.lib.enums.TA_CENTER
        elif (align == 'JUSTIFY'):
            res = reportlab.lib.enums.TA_JUSTIFY
        elif (align == 'RIGHT'):
            res = reportlab.lib.enums.TA_RIGHT
        else: 
            res = reportlab.lib.enums.TA_LEFT

        return res
    
        
    def get_font(self, column_data):
        """ return the font to use for this cell. Depending on columns settings and this cell """
        if self.font != None:
            return self.font
        else:
            return column_data.font
    
    
    def get_font_size(self, column_data):
        """ return the font size to use for this cell. Depending on columns settings and this cell """
        if self.font_size != None:
            return self.font_size
        else:
            return column_data.font_size
    
    
    def get_alignment(self, column_data):
        """ return the alignment to use for this cell, dependinh on column settings """
        if self.align != None:
            return self.align
        
        if column_data.align != None:
            return column_data.align
        
        return self.default_align
    
    
    def get_background_color(self, column_data):
        """return the color of the background. None for no background """
        
        if self.background_color != None:
            return self.background_color
        
        if column_data.background_color != None:
            return column_data.background_color
        
        return None
        

    def get_style(self, column_data):
        """ return special styles for this cell. 
            for exemple: [
                ('VALIGN','TOP')
                ('TEXTCOLOR','#ff0000'),
                ('INNERGRID', 0.25, '#ffff00'),
                ]        
        """
        styles = []
        
        background = self.get_background_color(column_data)
        if background != None:
            styles.append(('BACKGROUND', background))
        
        return styles


class ColData(object):  
    """ this class define a column of the table 
        do not use it directly, call SimpleRowsTableData.add_column() instead
    """
    _title = ""
    _width = 'auto'
    align= None
    background_color = None
    
    #titles font
    header_font = 'Helvetica-Oblique'    
    header_font_size = 8    
    
    #data font
    font = 'Helvetica'
    font_size = 8
        
    _my_pos = None
    accepted_cell = CellData
    
    def __init__(self, title="", width='auto'):
        """ constructor
            title = column name """
        self._title = title
        self._width = width
        self._my_pos = None
        
    def get_title(self):
        """return the title of the col"""

        ps = ParagraphStyle('header')
        ps.fontName = self.header_font
        ps.fontSize = self.header_font_size
        ps.alignment = self.get_align_code()
        
        return Paragraph(self._title, ps)
    
    
    def get_content_special_style(self):
        """ return a list of special styles to apply to this column's data. 
            a style is define by a tuple as thoses used by reportlab but without coordinates informations
            
            for exemple: [
                ('VALIGN','TOP')
                ('TEXTCOLOR','#ff0000'),
                ('INNERGRID', 0.25, '#ffff00'),
                ]
        """
        
        
        return []

    def get_header_special_style(self):
        """ return a list of special styles to apply to this column's header. 
            a style is define by a tuple as thoses used by reportlab but without coordinates informations
            
            for exemple: [
                ('VALIGN','TOP')
                ('TEXTCOLOR','#ff0000'),
                ('INNERGRID', 0.25, '#ffff00'),
                ]        
        """
        
        return []
    
    def get_align_code(self):
        """return the reportlab code corresponding to the alignement """
        
        if (self.align == 'CENTER'):
            res = reportlab.lib.enums.TA_CENTER
        elif (self.align == 'JUSTIFY'):
            res = reportlab.lib.enums.TA_JUSTIFY
        elif (self.align == 'RIGHT'):
            res = reportlab.lib.enums.TA_RIGHT
        else: 
            res = reportlab.lib.enums.TA_LEFT

        return res    
    
        
class TextCellData(CellData):
    """ a cell of the table that contain text 
        do not use it directly, call SimpleRowsTableData.add_text_cell() instead            
    """
    truncate_length = None
    indent = None
        
    def __init__(self, value, truncate_length=None, indent=None):
        """ constructor
            value = cell's content
            truncate_length = truncate the cell content to this length
            indent= left indentation of the cell content
        """
        self.truncate_length = truncate_length
        self.indent = indent
        super(TextCellData, self).__init__(value)
    
    def get_content(self, column_data, row_values, col_values):
        """ return the content formated as defined in the constructor or in the column object """
        value = self.value
        
        if value == None or value == False:
            return ""
        
        #should we trunc the text
        if self.truncate_length != None:
            value = c2c_helper.ellipsis(value, self.truncate_length, ellipsis="[...]")

        ps = ParagraphStyle('standard_text')
        ps.fontName = self.get_font(column_data)
        ps.fontSize = self.get_font_size(column_data)
        ps.alignment = self.get_align_code(column_data)

        
        #should we indent the content
        if self.indent != None:
            ps.leftIndent = self.indent * 2 * mm
        elif type(column_data) == TextColData and column_data.indent != None:
            ps.leftIndent = column_data.indent * 2 * mm
        
        p = Paragraph(c2c_helper.encode_entities(value), ps)
        return p
        
        
class TextColData(ColData):
    """ this class contain a column that contain text values 
        do not use it directly, call SimpleRowsTableData.add_text_column() instead
    
    """
    truncate_length = None
    indent = None
    accepted_cell = TextCellData
    align= 'LEFT'
    
    def __init__(self, title="", width='auto', truncate_length=None, indent=None):
        """ constructor
            title = column name
            truncate_length = truncate the column content to this length. Can be override by the cell object
            indent= left indentation of the column content. Can be override by the cell object
        """
        self.truncate_length = truncate_length
        self.indent = indent
        super(TextColData,self).__init__(title, width)    
    
    
class NumCellData(CellData):
    """ a cell of the table that contain numerical data 
        do not use it directly, call SimpleRowsTableData.add_num_cell() instead                
    """
    default_align = 'RIGHT'
    separator = None
    decimal= None
    
    def __init__(self, value, decimals=2, separator="'"):
        """ constructor
            value = cell's content
            decimal = number of digits after the comma
            separator = thousand separator
        """
        self.separator = separator
        self.decimals = decimals
        super(NumCellData, self).__init__(value)
        
    def _get_instant_value(self, column_data, row_values, col_values):
        return self.value
        
    def get_raw_content(self, column_data, row_values, col_values):
        """return the content of the cell without paragraph styles"""
        

        separator = None
        decimals = None
        content = ""
        if self.value == None:
            return ""
        
        #handle the separator (either from the column definition or from the cell definition)
        if self.separator != None: 
            separator = self.separator
        elif type(column_data) == NumCellData and column_data.separator != None:
            separator = column_data.separator
            
        #handle the decimals (either from the column definition or from the cell definition)
        if self.decimals != None:
            decimals = self.decimals
        elif type(column_data) == NumCellData and column_data.decimals != None:
            decimals = column_data.decimals

        res= c2c_helper.comma_me(self._get_instant_value(column_data, row_values, col_values), decimals=decimals, separator=separator)

        return res
    
    
    def get_content(self, column_data, row_values, col_values):
        """ return the content of the cell, formated as define in the constructor or in the column object """
     
        res = self.get_raw_content(column_data, row_values, col_values)
        
        ps = ParagraphStyle('num_cell')
        ps.fontName = self.get_font(column_data)
        ps.fontSize = self.get_font_size(column_data)
        ps.alignment = self.get_align_code(column_data)
        res = Paragraph(res, ps)                 
            
        return res
    
    
    
class NumColData(ColData):
    """ this class define a column that contain numerical values 
        do not use it directly, call SimpleRowsTableData.add_num_column() instead    
    """
    decimals = None
    separator = None
    align= 'RIGHT'
    
    accepted_cell = NumCellData

    def __init__(self, title="", width='auto', decimals=2, separator="'"):
        """ constructor
            tiltle = column name
            decimals = number of digits after the comma
            separator= thousand separator
        """
        self.decimals = decimals
        self.separator = separator
        super(NumColData, self).__init__(title, width)
    
    
class MoneyCellData(NumCellData):
    """ a cell that contain monetary data 
        do not use it directly, call SimpleRowsTableData.add_money_cell() instead                
    """
    currency = None
    
    def __init__(self, value, currency=None, decimal=2, separator="'"):
        """ constructor
            value = cell's content
            currency = 3 chars to define the currency
            decimal = number of digits after the comma
            separator = thousand separator
        """
        self.currency = currency
        super(MoneyCellData, self).__init__(value, decimal, separator)
    
    
    
    def get_content(self, column_data, row_values, col_values):
        """ return the content formated as defined in the constructor or in the column """
        
        res = self.get_raw_content(column_data, row_values, col_values)
        
        if res == None or res == False or res == "":
            return ""
        
        res += " "+self.get_currency(column_data)
        ps = ParagraphStyle('money_cell')
        ps.fontName = self.get_font(column_data)
        ps.fontSize = self.get_font_size(column_data)
        ps.alignment = self.get_align_code(column_data)
        res = Paragraph(c2c_helper.encode_entities(res), ps)                 
        
        
        return res
    
    
    
    def get_currency(self, column_data):
        """ return the font size to use for this cell. Depending on columns settings and this cell """
        
        result = None
        if self.currency != None:
            result = self.currency
        elif column_data.currency != None:
            result = column_data.currency    
        else: 
            result = ""
            
        return result
             
        
        
class MoneyColData(NumColData):
    """ this class define a column that contain monetary values 
        do not use it directly, call SimpleRowsTableData.add_money_column() instead    
    """
    currency = None
    accepted_cell = MoneyCellData
    
    def __init__(self, title="", width='auto', currency="", decimals=2, separator="'"):
        """ constructor
            title = column name
            currency = three letters abreviation for the currency
            decimals = number ofdigits after the comma
            separator = char used to separate thousands
        """
        self.currency = currency
        super(MoneyColData, self).__init__(title, width, decimals, separator)


class DateCellData(CellData):
    """ a cell that contain a date
        do not use it directly, call SimpleRowsTableData.add_date_cell() instead                    
    """
    format = None
    default_align= 'RIGHT'    
    
    DEFAULT_FORMAT = "%d.%m.%Y"
    
    def __init__(self, value, format=None):
        """constructor
           value = the cell content
           format = the date format
        """
        
        self.format = format
               
        val = value
        #assume the date comes from the database if it's a string
        if type(val) == str:
            val = time.strptime(val, "%Y-%m-%d")
            
        super(DateCellData, self).__init__(val)
    
    
    def get_content(self, column_data, row_values, col_values):
        """return the content formated as defined in the constructor or in the column """
        
        if self.value == None or self.value == False:
            return ""
                
        format = self.DEFAULT_FORMAT
        if self.format != None:
            format = self.format
        elif type(column_data) == DateColData and column_data.format != None:
            format = column_data.format
        
        value = super(DateCellData,self).get_content(column_data, row_values, col_values)
                
        if format != None:
            value = time.strftime(format, value)
        else: 
            value = time.strftime(self.format, value) 

        
        ps = ParagraphStyle('date_cell')
        ps.fontName = self.get_font(column_data)
        ps.fontSize = self.get_font_size(column_data)
        ps.alignment = self.get_align_code(column_data)
        res = Paragraph(c2c_helper.encode_entities(value), ps)                 
        
        return res
        



class DateColData(ColData):
    """ this class define a column that contain dates 
        do not use it directly, call SimpleRowsTableData.add_date_column() instead    
    """
    
    accepted_cell = DateCellData
    format = None
    align= 'RIGHT'
    
    def __init__(self, title="", width='auto', format="%d.%m.%Y"):
        """ constructor
            title = column name
            format = date format
        """
        self.format = format
        super(DateColData, self).__init__(title, width)



class NestedTableCellData(CellData):
    """ add a cell that contain lists of values. See add_nested_columns() for details. 
        pass to the constructor a SimpleRowsTableBuilder object that contain column definitions and values for this row.
        do not use it directly, call SimpleRowsTableData.add_nested_cells() instead    
    """

    _tableBuilder = None

    def __init__(self, tableBuilder):
        """ constructor  """
        self._tableBuilder = tableBuilder
        self._tableBuilder.width = "100%"
        self._pos = None
        super(NestedTableCellData, self).__init__(None)
    
    
    def get_content(self, column_data, row_values, col_values):
        
        data = self._tableBuilder._get_data_rows()
        width  = self._tableBuilder._get_columns_width()

        if len(data) == 0:
            return ""
        
        content = Table(data, width)
        
        styles = []
        styles += self._tableBuilder._get_standard_styles()
        styles += self._tableBuilder._get_data_styles(0)
        content.setStyle(styles)
        
        
        return content



class NestedTableColData(ColData): 
    """ add nested column(s) to a table. Nested columns are columns that contain multiple rows of data for each main row.
        - Using one nested column allow to create a column that contain lists of values for each rows. 
        - Using more that one nested columns allow to have matching lists that stay aligned whatever they contain on each row
        pass to the constructor a SimpleRowsTableBuilder object that contain only columns definitions and no data
        do not use it directly, call SimpleRowsTableData.add_nested_columns() instead    
    """    
    
    accepted_cell = NestedTableCellData
    _tableBuilder = None

    def __init__(self, tableBuilder, width='auto'):
        """ constructor """
        
        self._tableBuilder = tableBuilder
        self._tableBuilder.width = "100%"
        
        super(NestedTableColData, self).__init__(None, width)    


    def get_title(self):
        """return the title of the col. it returns a table"""
        
        insideTable = []
        
        
        headers = self._tableBuilder._get_header_row()
        width  = self._tableBuilder._get_columns_width()
        
        content = Table([headers], width)                 
            
        styles = []
        styles += self._tableBuilder._get_standard_styles()
        styles += self._tableBuilder._get_headers_styles(0)
        content.setStyle(styles)
        
        return content
    
    
    def get_header_special_style(self):
        """ special style for the header cell """
        
        # disable padding of the main table. the padding of the inner table is enough
        return [('LEFTPADDING', 0),
                ('RIGHTPADDING', 0),
                ('BOTTOMPADDING', 0),
                ('TOPPADDING', 0),              
                ]
        
    def get_content_special_style(self):
        """ return styles for this column content """
        
        # disable padding. the padding of the inner table is enough
        return [('LEFTPADDING', 0),
                ('RIGHTPADDING', 0),
                ('BOTTOMPADDING', 0),
                ('TOPPADDING', 0),  
                ]


class HeaderCellData(TextCellData):
    """ add a cell in a header Column. This cell is a text cell but with oblique text """
    
    font = 'Helvetica-Oblique'
    

class HeaderColData(TextColData):
    """ a column header which is a text column but with header styles 
        it is used in key_values_table to define header columns
    """
    accepted_cell = HeaderCellData
    align= 'LEFT'
    
    def get_content_special_style(self):
        """ return styles for this column content """
        
        return [('FONTNAME', self.DEFAULT_HEADER_FONT)]


    def get_content_special_style(self):
        """ return styles for this column content """
        
        # disable padding. the padding of the inner table is enough
        return [('BOX', 1, colors.black),
                ]

    

class SubtotalNumCellData(NumCellData):
    """  a cell that will display the total of above cells  (display is bold) """
    
    font = "Helvetica-Bold"
    font_size = 8
    
    def __init__(self, decimal=2, separator="'"):
        """ constructor """
        super(SubtotalNumCellData, self).__init__(0, decimal, separator)
        
    
    def _get_instant_value(self, column_data, row_values, col_values):
        """ return the total of the above cells """
        
        total = 0
        for c in col_values:
            total += c.value
        
        return total
    
    
    def get_content(self, column_data, row_values, col_values):
        """ return the content of the cell, formated as define in the constructor or in the column object """
     
        res = self.get_raw_content(column_data, row_values, col_values)
        
        ps = ParagraphStyle('tot_cell')
        ps.fontName = self.get_font(column_data)
        ps.fontSize = self.get_font_size(column_data)
        
        #handle the alignment (if defined and different from the column alignement)
        ps.alignment = self.get_align_code(column_data)
            
        res = Paragraph(res, ps)                 
        return res    






class SubtotalMoneyCellData(SubtotalNumCellData):
    """  a cell that will display the total of above cells  as a money value (with a currency) (display is bold) """

    currency = None
    
    def __init__(self, currency=None, decimal=2, separator="'"):
        self.currency = currency
        super(SubtotalMoneyCellData, self).__init__(decimal, separator)

    
    def get_currency(self, column_data):
        """ return the font size to use for this cell. Depending on columns settings and this cell """
        
        result = None
        if self.currency != None:
            result = self.currency
        elif column_data.currency != None:
            result = column_data.currency    
        else: 
            result = ""
            
        return result
    
    
    def get_content(self, column_data, row_values, col_values):
        """ return the content formated as defined in the constructor or in the column """

        res = self.get_raw_content(column_data, row_values, col_values)

        if res == None:
            return ""
        
        res += " "+self.get_currency(column_data)

        ps = ParagraphStyle('tot_money_cell')
        ps.fontName = self.get_font(column_data)
        ps.fontSize = self.get_font_size(column_data)
        
        #handle the alignment (if defined and different from the column alignement)
        ps.alignment = self.get_align_code(column_data)
        
        res = Paragraph(res, ps)     
        return res            
        
    