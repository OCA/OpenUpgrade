# -*- coding: utf-8 -*- 
##############################################################################
#
# Copyright (c) Camptocamp SA - http://www.camptocamp.com
# Author: Arnaud Wüst
#
#
#    This file is part of the c2c_report_tools module
#    It contains the following class:
#
#    - TimeBoxesChartBuilder: a factory to create the timeboxes chart
#                               - On X: dates, On Y: text items.
#                               - In the chart boxes that define time periods for Y items
#
#    - TimeBoxesChartLegendBuilder same chart but with an additionnal color legend.
#
#    see c2c_planning_management for exemples.
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

from datetime import datetime, timedelta
from reportlab import platypus
from reportlab.platypus import *
from reportlab.lib.units import mm
from reportlab.lib import colors

from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase.pdfmetrics import stringWidth

from reportlab.lib.enums import *

import time
from c2c_reporting_tools.c2c_helper import *
from c2c_reporting_tools.flowables.color_legend import *
from c2c_reporting_tools.translation import _

class TimeBoxesChartBuilder(object):
    """ Tool to generate a graphical object to be displayed in rapports
        on X: time defined by date_start and date_end in the constructor
        on Y: A list of items defined by TimeBoxesChartBuilder.append_Y_item()
        in the chart: periods defined by TimeBoxesChartBuilder.add_period()
        usage: - create a an object of this class.
               - add Y items with TimeBoxesChartBuilder.append_Y_item()
               - add time boxes with TimeBoxesChartBuilder.add_period()
               - then get the chart object with TimeBoxesChartBuilder.get_flowable() and insert it in the story of a template.
    """


    FIRST_COLUMN_WIDTH = 50*mm
    
    HEADER_ROWS = 3 #NBR OF ROWS REPETED PAGES PER PAGES
    
    #constants
    DEFAULT_TIMEBOX_COLOR = "#bbbbbb"
    DEFAULT_FONT = "Helvetica"
    DEFAULT_FONT_SIZE = 8
    INDENT_SPACE = 1*mm


    width = 0 #table width
    data = None #data that define the chart
    table = None #list of lists that represent chart cells
    styles = [] #list of styles to apply to the table
    
    
    def __init__(self, title="", date_start=None, date_end=None):
        """ "title" will appear in the first line of the array (the grayed one)
            "date_start" (datetime object) define where the X axis should start. Leave it empty to let the chart autoscale on the datas. 
            "date_end" (datetime object) define where the Y axis should end. Leave it empty to let the chart autoscall on the datas
        """
        self.width = 0
        self.table = []
        self.styles = []
        self.data = TimeBoxesChartData(title, date_start, date_end)
    
    def enable_translations(self, cr, context):
        """ pass a cr object and a context dictionnary that contain the 'lang' key to this method to allow label translations 
            otherwise, labels (such as scales names) stay in english """
        
        #I do it this way because translations only work where cr and context are defined
        translations = {}
        translations['Years']  = _('Years')
        translations['Months'] = _('Months')
        translations['Weeks']  = _('Weeks')
        translations['Days']   = _('Days')
        
        self.data.set_translations(translations)
        
        
    def append_Y_item(self, text, indent=0, id=None, color=None):
        """ add an element to the Y axis of the chart. Either give an id to reference it or retrieve the id of the new element from the return 
            it will raise an error if you specifiy an id that already exists
            "indent" define the level of indentation of the text
            "color" define the default color of the boxes for this line. 
                    accepted formats: reportlab.lib.colors.red
                                      "red"
                                      (0.2, 0.5, 0.8)
                                      "#ccffdd"
                                      
            to add style to the item's text, you can enclose the text into rml tags. 
                examples: '<b>'+your_text+'</b>' will display the text in bold
                          '<para textColor="red">'+your_text+'</para>' will display the text in red
        """
        return self.data.append_Y_item(text, indent, id, color)
        
    
    
    def add_period(self, item_id, date_start, date_end, color=None, text=None, grid=None):
        """ add a period to the graph at the line referenced by "item_id" from the date date_start to the date date_end. Both date are datetime elements. 
            raise an error if the item_id does not exists. Add the item first with append_Y_item 
            "color" define a color for this timebox. It can override the color define for the line in append_Y_item
                    accepted color formats: reportlab.lib.colors.red
                                            "red"
                                            (0.2, 0.5, 0.8)
                                            "#ccffdd"
            "grid" also accept a color
        """
        return self.data.add_period(item_id, date_start, date_end, color, text, grid)
    
    
    def get_flowable(self, width):
        """ return the chart object built with append_Y_item() and add_period() 
            the returned object is a reportlab flowable object that can be passed to a template for rendering
        """
        
        self.width = width 
    
        #now the all items and all periods are added, let's process everything to prepare the data to be draw
        self.data.prepare_and_scale()
        
        #let's format datas into a format (table struct and styles) that is usable in reportLab objects
        self._build_empty_table()
        self._add_title()
        self._add_secondary_scale()
        self._add_main_scale()
        self._add_Y_items()
        self._add_periods()
          
        #self.table and self.styles are ready to be used to create the flowable object
        column_width = self._compute_columns_widths(self.table)
        chart =  TimeBoxesChartTable(self.table, column_width, repeatRows= self.HEADER_ROWS)
        chart.setStyle(TableStyle(self.styles))
        
        return chart
        
        
        
    def get_boundary_dates(self):
        """ return the boundrary dates of the graphic. Define either by the dates given to the constructor or by the data (see add_period() ) """
        return self.data.get_boundary_dates()

    def set_title(self, title):
        """ redefine the title passed in the construtor """
        self.data.title = title


    def _build_empty_table(self):
        """ create a bi-dimentional list the represent the chart table. do not add anything in cells"""
        self.table = []
        
        table_length = len(self.data.scale.scale_items) + 1
        #title and two rows of scale
        for i in range(3):
            self.table.append((table_length) * [''])
  
        #rows for items 
        for i in range(self.data.lines_number):
            self.table.append((table_length) * [''])

        #global font for the whole graphic
        self.styles.append(('FONT', (0,0), (-1,-1),self.DEFAULT_FONT, self.DEFAULT_FONT_SIZE))
        # main frame arround the whole table
        self.styles.append(('BOX', (0,0), (-1,-1), 1, colors.black))
        #in cells, text start in the top left corner
        self.styles.append(('VALIGN', (1,self.HEADER_ROWS), (-1,-1), 'MIDDLE'))

        
        
        
    def _add_title(self):
        """add the title (text and style) to the table """
        
        #title in the first cell of the first row
        self.table[0][0] = self.data.title
        
        
         #title border
        self.styles.append(('BOX', (0,0), (-1,0), 1, colors.black))
        #title background
        self.styles.append(('BACKGROUND', (0,0), (-1,0), '#bbbbbb'))



    def _add_secondary_scale(self):
        """ add the secondary scale to the table (text + styles) """
        
        Y_pos = 1
        X_pos = 1
    
    
        #write the label
        ps = ParagraphStyle('secondary_scale_label')
        ps.alignment = TA_RIGHT
        ps.fontName = self.DEFAULT_FONT
        ps.fontSize = self.DEFAULT_FONT_SIZE

        title = Paragraph(self.data.scale.secondary_label, ps)
        self.table[Y_pos][0] = title
    
        
        
        ps = ParagraphStyle('secondary_scale')
        ps.alignment = TA_CENTER
        ps.fontName = self.DEFAULT_FONT
        ps.fontSize = self.DEFAULT_FONT_SIZE
                  
        #the secondary scale is not define the same way as the primary scale. 
        #it's defined by groups of same label. (start_pos, start_end, item)
        # see ScaleData._group_scale() for details
        for group in self.data.scale.secondary_scale_groups:
            pos_start, pos_end, item = group
            p = Paragraph(item, ps)
            
            #draw the label in the middle of the similar cells
            self.table[Y_pos][int((pos_start+pos_end)/2)+1] = p
            
            #draw light border arrounds items
            self.styles.append(('BOX', (pos_start+X_pos,Y_pos), (pos_end+X_pos,Y_pos), 0.2, "#bbbbbb"))
            
        
        

    def _add_main_scale(self):
        """ add the main scale to the table (text + style) """
        
        Y_pos = 2
        X_pos = 1
        
        
        #write the label
        ps = ParagraphStyle('scale_label')
        ps.alignment = TA_RIGHT
        ps.fontName = self.DEFAULT_FONT
        ps.fontSize = self.DEFAULT_FONT_SIZE

        title = Paragraph(self.data.scale.main_label, ps)
        self.table[Y_pos][0] = title

        
        
        ps = ParagraphStyle('scale')
        ps.alignment = TA_CENTER
        ps.fontName = self.DEFAULT_FONT
        ps.fontSize = self.DEFAULT_FONT_SIZE
        
        #reduce the size of the font for large scales
        if len(self.data.scale.scale_items) > 80: 
            ps.fontSize = 6
        
        #add labels for each scale item
        #also add weekend grayed column
        cpt = X_pos
        for item in self.data.scale.scale_items:
            p = Paragraph(item, ps)
            self.table[Y_pos][cpt] = p
            
            #handle weekemd
            if self.data.scale.weekend[cpt-X_pos]:
                #light grey columns 
                self.styles.append(('BACKGROUND', (cpt,Y_pos), (cpt,-1), "#dddddd"))
            
            
            cpt+= 1


        #light grid beetween     
        self.styles.append(('INNERGRID', (X_pos,Y_pos), (-1,Y_pos), 0.2, "#bbbbbb"))
        #line that separate the dates and the datas
        self.styles.append(('LINEBELOW', (0, Y_pos), (-1,Y_pos), 1, colors.black))
           


    def _add_Y_items(self):
        """ add Y items labels to the chart (Text and styles). Add also light grid for their lines """
        
        X_pos = 0
        Y_pos = 3

        #draw the items titles with the right indentation

        for i in self.data.items_order:
            
            item = self.data.items[i]
            
            ps = ParagraphStyle('indent')
            ps.fontName = self.DEFAULT_FONT
            ps.fontSize = self.DEFAULT_FONT_SIZE
            ps.leftIndent = item.indent * self.INDENT_SPACE
            
            p = Paragraph(self._encode_entities(item.label), ps)
            self.table[Y_pos + item.Y_pos][X_pos] = p
            
            #draw the inner grid for this lines 
            start_X = X_pos
            end_X = -1
            start_Y = Y_pos + item.Y_pos
            end_Y = Y_pos + item.Y_pos + item.line_number
            self.styles.append(('LINEABOVE', (start_X, end_Y), (end_X, end_Y), 0.2, "#bbbbbb"))
            self.styles.append(('LINEAFTER', (start_X, start_Y), (end_X, end_Y), 0.2, "#bbbbbb"))
            
        #line that separate the Y items and the datas
        self.styles.append(('LINEAFTER', (X_pos, Y_pos-2), (X_pos, -1), 1, colors.black))


    def _add_periods(self):
        """ draw periods' boxes in the chart. with text and style """
        
        X_pos = 1
        Y_pos = 3
        
        #for each Y item
        for i in self.data.items_order:
            # for each period of this item
            for period in self.data.items[i].periods:
                
                #find the box's color
                color = period.color
                #if the color of the period is not define, 
                if period.color == None:
                    #try to use the color of the line 
                    if self.data.items[i].color != None:
                        color = self.data.items[i].color                
                    #if no color are define, use default ones
                    else: 
                        color = self.DEFAULT_TIMEBOX_COLOR
                        
                #find the grid color
                #if the grid color is not defined
                grid = period.grid
                if period.grid == None:
                    grid = color
                


                #handle time strcut and datetimes
                date_start = period.date_start
                if isinstance(date_start,time.struct_time):
                    date_start = datetime.datetime(*date_start[:3])                   
                date_start = date_start.replace(hour=0, minute=0, second=0, microsecond=0)
                date_end = period.date_end
                if isinstance(date_end,time.struct_time):
                    date_end = datetime.datetime(*date_end[:3])
                date_end = date_end.replace(hour=0, minute=0, second=0, microsecond=0)
                    
                
                X_start = X_pos + period.scale_item_start
                X_end = X_pos + period.scale_item_end
                Y_start = Y_pos + self.data.items[i].Y_pos + period.offset
                Y_end = Y_start
                #draw the period in the right color
                self.styles.append(('BACKGROUND', (X_start, Y_start), (X_end, Y_end), color))
                self.styles.append(('INNERGRID', (X_start, Y_start), (X_end, Y_end), 0.3, grid))

                self.styles.append(('BOX', (X_start, Y_start), (X_end, Y_end), 0.2, colors.black))
                self.styles.append(('LEFTPADDING', (X_start, Y_start), (X_end, Y_end), 2))
                
                
                
                self.table[Y_start][X_start] = self._trunc_label(period.label, period.scale_item_end - period.scale_item_start + 1)



    def _trunc_label(self, text, period_size):
        """ trunc a period's label depending on the size of the period 
            "period_size" is an integer: the number of scale items between period's start and period's end dates
        """
        
        if text == None :
            return ""
        if len(text) <= 1:
            return text
        
        # find the width of a column
        columns_width = self._compute_columns_widths(self.table)
        column_width = columns_width[1]
        
        period_width = column_width * period_size

        string_width = stringWidth(text, self.DEFAULT_FONT, self.DEFAULT_FONT_SIZE)
        
        margin_width = stringWidth(" .", self.DEFAULT_FONT, self.DEFAULT_FONT_SIZE)

        cpt = len(text)
        
        #if the width of the text is greater than the width of the period, try to remove a char at the end and start again.
        #TOOD: could be improved to do less loops (dichotomic tests...)
        tmp_text = text
        while cpt > 1 and string_width + margin_width > period_width:
            cpt -= 1
            
            #string from db are encoded in utf8....
            tmp_text = text.decode('utf-8')
            #...  but text operation are ascii... 
            tmp_text= tmp_text[0:cpt]
            # ... and reportlab work in utf8 too.... 
            tmp_text = tmp_text.encode('utf-8')

            string_width = stringWidth(tmp_text, self.DEFAULT_FONT, self.DEFAULT_FONT_SIZE)     
            
        result = tmp_text
        
        #add a final . to truncated texts
        if cpt < len(text):
            result += "."
        return result
               
        

    def _encode_entities(self, s):
        """replace problem smybols with their code"""
        
        return c2c_helper.encode_entities(s)

        
    def _compute_columns_widths(self, table):
        """construct the list of column width. They have all the same size except the first one """
        
        return [self.FIRST_COLUMN_WIDTH] + ((len(table[0]) -1) * [(self.width -self.FIRST_COLUMN_WIDTH) / (len(table[0]) -1)])    



class TimeBoxesChartLegendBuilder(TimeBoxesChartBuilder):
    """ a timeboxes chart with a color legend"""
    
    colors_legend = None
    
    def __init__(self, title="", legend_title=None, date_start=None, date_end=None):

        self.colors_legend = ColorLegendBuilder(legend_title)
        super(TimeBoxesChartLegendBuilder, self).__init__(title, date_start, date_end)
    
    
    def add_period(self, item_id, date_start, date_end, color=None, text=None, group_text=None, grid=None):
        """ add a period. see TimeBoxesChartBuilder.add_period() for details """
        legend_text = text
        if group_text != None:
            legend_text = group_text
        
        color_id = self.colors_legend.add_unique_item(legend_text, color)
        box_color = self.colors_legend.get_color(color_id)
        super(TimeBoxesChartLegendBuilder, self).add_period(item_id, date_start, date_end, box_color, text, grid)
    
    def get_legend_flowable(self, width):
        """ return the flowable object that represent the color legend for the chart """
        return self.colors_legend.get_flowable(width)
    
    def append_Y_item(self, text, indent=0, id=None):
        """ add an item on the Y axis. see TimeBoxesChartBuilder.append_Y_item() for details
            this method does not allow to define color for a whole lines (because it would not make sens with a color legend
        """
        return super(TimeBoxesChartLegendBuilder, self).append_Y_item(text, indent, id, None)



  
class TimeBoxesChartData(object):
    """ a data containter internaly used by the timeBoxesChartBuilder object. """
    
    
    title = ""
    date_start = None
    date_end= None
    
    items = {}
    items_order = []
    
    scale = None
    lines_number = None #total number of lines needed to draw the chart
    
    translations = {}

    
    def __init__(self, title, date_start=None, date_end=None):
        """ "title" will appear in the first line of the array (the grayed one)
            "date_start" (datetime object) define where the X axis should start. Leave it empty to let the chart autoscale on the datas. 
            "date_end" (datetime object) define where the Y axis should end. Leave it empty to let the chart autoscall on the datas
            "translations" can contain translations for label texts
        """

        self.title = title
        if isinstance(date_start,time.struct_time):
            self.date_start = datetime.datetime(*date_start[:3])
        else:
            self.date_start = date_start
        if self.date_start != None:
            self.date_start = self.date_start.replace(hour=0, minute=0, second=0, microsecond=0)
    
        
        if isinstance(date_end,time.struct_time):
            self.date_end = datetime.datetime(*date_end[:3])
        else:
            self.date_end = date_end
        if self.date_end != None:
            self.date_end = self.date_end.replace(hour=0, minute=0, second=0, microsecond=0)
        
        
        self.items = {}
        self.items_order = []
        self.scale = None
        self.lines_number = None
    
        
    
    def set_translations(self, translations):
        """define the label translations """
        self.translations= translations
    
    def append_Y_item(self, text, indent=None, id=None, color=None):
        """ add an element to the Y axis of the chart. Either give an id to reference it or retrieve the id of the new element from the return 
            it will raise an error if you specifiy an id that already exists
            "text" is the label of the line
            "indent" define the level of indentation of the text
            "color" define the default color of the boxes for this line. 
                    accepted formats: reportlab.lib.colors.red
                                      "red"
                                      (0.2, 0.5, 0.8)
                                      "#ccffdd"
                                      
            to add style to the item's text, you can enclose the text into rml tags. 
                examples: '<b>'+your_text+'</b>' will display the text in bold
                          '<para textColor="red">'+your_text+'</para>' will display the text in red
        """
        
        item_id = None
                
        #id specified?
        if id != None:
            if id in self.items:
                raise Exception("Id already exists. Please use another id for this element (id= %s)" % id)
            item_id = id
        #find the next id
        else: 
            item_id = len(self.items)
            while item_id in self.items:
                item_id+= 1
            
            
        #store the text and the indentation
        self.items[item_id] = Yitem(text,item_id, indent, color)
        #store the order of the elements
        self.items_order.append(item_id)
        
        return item_id
        
        
        
    def add_period(self, item_id, date_start, date_end, color=None, text=None, grid=None):
        """ add a period to the graph at the line referenced by "item_id" from the date date_start to the date date_end. Both date are datetime elements. 
            raise an error if the item_id does not exists. Add the item first with append_Y_item 
            "color" define a color for this timebox. It can override the color define for the line in append_Y_item
                    accepted color formats: reportlab.lib.colors.red
                                            "red"
                                            (0.2, 0.5, 0.8)
                                            "#ccffdd"
            "text" will appear inside the timebox but will be truncated depending on the timebox length
            "grid" define the color of the grid. By default the grid is the same color as the box
        """ 
        
        #hack to solve compatibilty problems between python 2.4 and 2.5 in date handling
        if isinstance(date_start,time.struct_time):
            date_start = datetime.datetime(*date_start[:3])
        date_start = date_start.replace(hour=0, minute=0, second=0, microsecond=0)
            
        if isinstance(date_end,time.struct_time):
            date_end = datetime.datetime(*date_end[:3])
        date_end = date_end.replace(hour=0, minute=0, second=0, microsecond=0)
        
        
                
        #does the id exists? 
        if item_id not in self.items:
            raise Exception("Id does not exists. Please add first the related item with append_Y_item. (id= %s) " %item_id)
        
        #is the period valid? 
        if date_end < date_start:
            raise Exception("Invalid period definition, date end before date start: date_start: %s, date_end %s " % (date_start, date_end))
        
        #ignore periods out of scale range
        if self.date_start != None and date_end < self.date_start \
            or self.date_end != None and date_start > self.date_end:
            pass
        
        else:
            #truncate the period if it goes beyond the limits
            if self.date_start != None and date_start < self.date_start:
                date_start = self.date_start
            if self.date_end != None and date_end > self.date_end:
                date_end = self.date_end
        
            #store the period
            return self.items[item_id].add_period(date_start, date_end, text, color, grid)


    def prepare_and_scale(self):
        """ this method is called after all append_Y_item and add_periods to prepare the data to be used to draw the chart
            it matches the scales and the Y items to define indexes that will be used to draw periods
        """
        
        
        (date_start, date_end) = self.get_boundary_dates()
        #compute the scale
        self.scale = ScaleData(date_start, date_end, self.translations)       

        #now the scale is defined, the Y items can define how many lines they need to display their periods
        for i in self.items_order:
            self.items[i].scale_on(self.scale)
            
        #now the items defined theirs needs in terms of lines, we can do a mapping between items id and position in the chart lines
        cpt = 0
        for i in self.items_order:
            #define the Y pos of each Y item
            self.items[i].Y_pos = cpt
            #take in account multi-lines Y items
            line_cpt = 0
            while line_cpt < self.items[i].line_number:
                cpt+=1
                line_cpt+=1        
                
        #just store the whole number of lines needed by this chart
        self.lines_number = cpt
        

        

    def get_boundary_dates(self):
        """ return the boundrary dates of the graphic. Define either by the dates given to the constructor or by the data (see () ) """
        
        #if both date are defined in the constructor, no need to search for boundary dates in the datas
        if self.date_start != None and self.date_end != None: 
            return (self.date_start, self.date_end)
        
            
        #go through all the datas to find the first and last date
        max_date = None
        min_date = None
        for item_id in self.items_order:
            for period in self.items[item_id].periods:
                if max_date == None or max_date < period.date_end:
                    max_date = period.date_end
                if min_date == None or min_date > period.date_start:
                    min_date = period.date_start
        
        #dates define in the constructor have priority of those defined by periods
        if self.date_start != None:
            min_date = self.date_start
        if self.date_end != None:
            max_date = self.date_end
            
        if isinstance(min_date,time.struct_time):
            min_date = datetime.datetime(*min_date[:3])
        min_date = min_date.replace(hour=0, minute=0, second=0, microsecond=0)

        if isinstance(max_date,time.struct_time):
            max_date = datetime.datetime(*max_date[:3])
        max_date = max_date.replace(hour=0, minute=0, second=0, microsecond=0)
                    
        return (min_date, max_date)
        
    
  

class TimeBoxesChartTable(Table):
    """ the flowable object returned by TimeBoxesChartBuilder->get_flowable() """
    
    def draw(self):
        """ called by the template engine to ask the table to draw itself"""
        
        #on each page, close the bottom table border
        self.setStyle(TableStyle([
                                  #line that separate the items and the datas
                                  ('LINEBELOW', (0, -1), (-1, -1), 1, colors.black),                                  
                                ]))
        
        Table.draw(self)
        
        
        
class Period(object):
    """ this class is period (a time box in the chart) """
    
    date_start = None
    date_end = None
    label = None
    color = None
    grid = None
    
    offset = 0
    scale_item_start = None
    scale_item_end = None
    
    
    def __init__(self, date_start, date_end, label=None, color=None, grid=None):
        """ constructor 
            "date_start" is the date when the period start
            "date_end" is the date when the period end
            "label" text to display in the period
            "color" color to draw the time box
            "grid" color to draw the timebox grid (None = same color as color)
        """
        
        self.date_start = date_start
        self.date_end = date_end
        self.label = label
        self.color = color
        self.grid = grid
        self.offset = 0
        self.scale_item_start = None
        self.scale_item_end = None
    
    
    def set_postition(self, scale_item_start, scale_item_end, offset):
        """allow to define where to start and end on the time scale and on which line of the Y item it will appears """
        
        self.scale_item_start = scale_item_start
        self.scale_item_end = scale_item_end
        self.offset = offset



class Yitem(object):
    """ this class contain all informations about an Y item and related periods """
    periods = []
    id = None
    label = None
    indent = None
    color = None
    line_number = None
    Y_pos = None
    lines = []
    
    
    def __init__(self, label, id, indent=None, color=None):
        """ constructor """
        self.periods = [] # list of all periods objects
        self.id = id # item's id
        self.label = label # text of this item
        self.indent = indent #indentation of the text
        self.color = color #default color for the boxes of this item
        
        self.line_number= None # number of lines this period will need
        self.Y_pos = None # position of the first line of this period in the chart table
        
    

    def add_period(self, date_start, date_end, text=None, color=None, grid=None):
        """ add a new period to this Y item """
        self.periods.append(Period(date_start, date_end, text, color, grid))        

    
    def scale_on(self, scaleData):
        """ map each of the periods defined for this Y item on the scale items.
            it means for each period's date_start and date_end, this function compute the start_scale_item and end_scale_item
            it compute also the number of lines needed by a Y item to display all periods without overlapping
            "scaleData" is filled ScaleData object
        """    
        
        max_level = 0
        lines = {}
        
        #go through all periods and find their position in the chart: where to start and end on the time scale and on which line of the Y item it will appears
        period_cpt = 0
        while period_cpt <  len(self.periods):
            
            #find the scale items matching the period's dates
            period_item_start= scaleData.get_scale_item(self.periods[period_cpt].date_start)
            period_item_end= scaleData.get_scale_item(self.periods[period_cpt].date_end)
                        
            tested_level = -1
            level_ok = False
            
            #find the first Y_item's line where there is enough room to put this period
            while not level_ok:
                level_ok = True
                tested_level += 1
                current_period_item = period_item_start
                #test the free room on this line for each scale's item covered by the period 
                while current_period_item <= period_item_end and level_ok:
                    if current_period_item in lines  and tested_level in lines[current_period_item]:
                        level_ok = False
                    current_period_item += 1
                
            #free level found! let's book it for the nexts periods
            
            current_period_item = period_item_start      
            #for each dates and for the previously found level, let's put a value in the 2D lists to book the room      
            while current_period_item <= period_item_end:
                if current_period_item not in lines:
                    lines[current_period_item] = {}
                if tested_level not in lines[current_period_item]:
                    lines[current_period_item][tested_level] = 1 # dummy value to hold fill the cell
                current_period_item += 1
            
            #define the position for the period 
            self.periods[period_cpt].set_postition(period_item_start, period_item_end, tested_level)
            period_cpt += 1
            
            if tested_level > max_level:
                max_level = tested_level
            
        #finally, define the number of lines this Y item will need    
        self.line_number = max_level + 1
            
         

class ScaleData(object):
    '''contain all the data that define the chart scale 
       this class is used internaly by the class TimeboxChartBuilder
    '''
    
    scale_items = [] # main scale
    secondary_scale_groups= [] #definition of the secondary scale
    scale_mapping = {} # mapping from each days between date_start and date_end to the corresponding scale item
    weekend = [] # list of items of the main scale that are saturday or sunday
    date_start = None #first day of the scale
    date_end = None # last day of the scale
    main_label = ""
    secondary_label = ""
    
    
    
    def __init__(self, date_start, date_end, translations={}):
        """constructor """

        #handle compatibility problems with dates between python 2.4 and 2.5
        if isinstance(date_start,time.struct_time):
            self.date_start = datetime.datetime(*date_start[:3])
        else:
            self.date_start = date_start
        self.date_start = self.date_start.replace(hour=0, minute=0, second=0, microsecond=0)
            
        if isinstance(date_end,time.struct_time):
            self.date_end = datetime.datetime(*date_end[:3])
        else:
            self.date_end = date_end
        self.date_end = self.date_end.replace(hour=0, minute=0, second=0, microsecond=0)
                
                
        self.scale_items, self.secondary_scale_groups, self.scale_mapping, self.weekend, labels = self._get_scale(self.date_start, self.date_end, translations)
        
        self.main_label = labels[0]
        self.secondary_label = labels[1]
        
        
    def get_scale_item(self, date):
        """return the scale item id corresponding to a given date. For exemple, if you pass the 09/09/2008 and the scale if based on weeks, it will return the scale item's id of the week 37 """
        return self.scale_mapping[date.strftime("%Y-%m-%d")]
        
    
    def _group_scale(self, scale):
        """ for a given scale, group similar elements and retrun a tuple that describe this groupment. 
            It is used to display nice secondary scales.
            return a list of tuples (star_pos, end_pos, item)
            
            Exemple:   ¦8¦8¦8¦8¦8¦8¦9¦9¦ will return ¦    8    ¦ 9 ¦
        """

        current_start_pos = None
        current_item = None
        current_end_pos = None
        cpt = 0
        
        groups = []
        
        for i in scale:            

            #if item change, it means we are at a limit
            if current_start_pos == None or current_item != i:
                #if start_pos is already defined, it means there is a group to close
                if current_start_pos != None:
                    current_end_pos = cpt -1
                    groups.append((current_start_pos, current_end_pos, current_item))

                current_start_pos = cpt
                current_item = i
                
            cpt += 1

        #add the last group that haven't been close
        groups.append((current_start_pos, cpt-1, current_item))
        return groups
        
        
    def _get_scale(self, date_start, date_end, translations={}):
        """return datas that define the scale to use in the display """


        #handle dates compatibility problems between python 2.4 and 2.5
        if isinstance(date_start,time.struct_time):
            date_start = datetime.datetime(*date_start[:3])
        date_start = date_start.replace(hour=0, minute=0, second=0, microsecond=0)
            
        if isinstance(date_end,time.struct_time):
            date_end = datetime.datetime(*date_end[:3])
        date_end = date_end.replace(hour=0, minute=0, second=0, microsecond=0)
            
            
        ##
        # depending on the number of days, define a scale and map a each days of the interval to a scale item
        #
        # for exemple, il the scale is defined by week, we could have this kind of mapping: 
        #         friday   09/05/2008 -> week 36
        #         saturday 09/06/2008 -> week 36
        #         sunday   09/07/2008 -> week 36
        #         monday   09/08/2008 -> week 37
        #         and so on...       
        #
        ##
        
        days_number = (date_end - date_start).days + 1
        
        scale = []
        secondary_scale = []
        date_mapping = {}
        weekend = []

        #1 scale item per day            
        if days_number <= 100:
            
            main_label = 'Days'
            if main_label in translations:
                main_label = translations[main_label]
                
            secondary_label = 'Months'
            if secondary_label in translations:
                secondary_label = translations[secondary_label]
                                        
            current_date = date_start
            cpt = 0
            while current_date <= date_end:
                #store the scale name
                scale.append(current_date.strftime("%d"))
                
                secondary_scale.append(current_date.strftime("%m"))
                #store for each date to wich scale item it is linked. (may sounds stupid for a scale by day as the mapping will be 1:1 but I do that to be consistant with other scales)
                date_mapping[current_date.strftime("%Y-%m-%d")] = cpt

                #if the day is a weekend, store it in the weekend dict to gray them
                if  current_date.weekday() in [5,6]:
                    weekend.append(True)
                else:                    
                    weekend.append(False)
                    

                #continue to next day
                cpt += 1
                current_date = current_date+timedelta(days=1)
                


        #1 scale item per week
        elif days_number <= 700 :
            
            main_label = 'Weeks'
            if main_label in translations:
                main_label = translations[main_label]
                
            secondary_label = 'Months'
            if secondary_label in translations:
                secondary_label = translations[secondary_label]
            
            #
            #find the monday of the week of date_start
            #
            week_number = str(int(date_start.strftime("%W")) -1)
            year = date_start.strftime("%Y")
            sunday_start = time.strptime(str(year)+"-"+str(week_number)+"-0","%Y-%W-%w")
            sunday_start = datetime.datetime(*sunday_start[:3])
            sunday_start = sunday_start.replace(hour=0, minute=0, second=0, microsecond=0)
            monday_start = sunday_start + timedelta(days=1)


            #
            #find the sunday of the week of date_end
            #
            
            #if the end date is not a saturday, find the next one
            if (date_end.strftime("%w") != "6"):                    
                week_number = int(date_end.strftime("%W")) + 1
                year = date_end.strftime("%Y")
                saturday_end_string = "%s-%s-%s" % (year, week_number, 6)
                saturday_end = time.strptime(saturday_end_string,"%Y-%W-%w")
                saturday_end = datetime.datetime(*saturday_end[:3])
            #the last day is a saturday, let's use it as the end date
            else: 
                saturday_end = date_end
                
            saturday_end = saturday_end.replace(hour=0, minute=0, second=0, microsecond=0)
            sunday_end = saturday_end + timedelta(days=1)
                    
            
            current_date = monday_start
            cpt=0
            
            while current_date <= sunday_end:
                #add new item in the scales
                
                #I do that the thursday to match the iso calendar rules
                if current_date.strftime("%w") == "4":
                    #store the weeknumber as the scale label
                    scale.append(str(current_date.isocalendar()[1]))
                    secondary_scale.append(current_date.strftime("%m"))
                                        
                #link each days to a scale item. 
                date_mapping[current_date.strftime("%Y-%m-%d")] = cpt
                    
                if current_date.strftime("%w") == "0":
                    cpt += 1
                    
                #continue to next day
                current_date = current_date+timedelta(days=1)
                
                #do not display grayed weekend days on week scale
                weekend.append(False)           
        #1 square per month
        elif days_number <= 2000 :
            main_label = 'Months'
            if main_label in translations:
                main_label = translations[main_label]
                
            secondary_label = 'Years'
            if secondary_label in translations:
                secondary_label = translations[secondary_label]
            
            
            def get_first_day(dt, d_years=0, d_months=0):
                """
                return the first day of the month
                found here: http://code.activestate.com/recipes/476197/
                """
                # d_years, d_months are "deltas" to apply to dt
                y, m = dt.year + d_years, dt.month + d_months
                a, m = divmod(m-1, 12)
                return datetime.datetime(y+a, m+1, 1,0,0,0)
            
            def get_last_day(dt):
                """
                return the last day of the month
                found here: http://code.activestate.com/recipes/476197/
                """
                return get_first_day(dt, 0, 1) + timedelta(-1)
            
            #find the 1 of the month of date_start
            start_1st_day = get_first_day(date_start)
            #find the last day of the month of date_end
            end_last_day = get_last_day(date_end)
            
            
            current_date = start_1st_day
            cpt=-1    
            while current_date <= end_last_day:
                #if it's the first day of the month
                if int(current_date.strftime("%d")) == 1:
                    #store the month number as the scale label
                    scale.append(current_date.strftime("%m"))
                    secondary_scale.append(current_date.strftime("%Y"))
                    cpt += 1
                    
                #link each days to a scale item. 
                date_mapping[current_date.strftime("%Y-%m-%d")] = cpt

                #do not display grayed weekend days on month scale
                weekend.append(False)           


                #continue to next day
                current_date = current_date+timedelta(days=1)
                
        else: 
            raise Exception("too much data to display on a page ( %s days), please choose a smaller date intervale (max 2000 days)" % days_number)
        
        return scale, self._group_scale(secondary_scale), date_mapping, weekend, (main_label, secondary_label)
        
