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
#    - ColorLegendBuilder: a factory to create the color legends for charts.
#                          
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
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.lib.enums import *
from c2c_reporting_tools.c2c_helper import *


class ColorLegendBuilder(object):
    """ this class allow to build a color legend for a chart. 
        it is also a tool to generate and manage colors for a chart (without necessary display the legend) """

    DEFAULT_FONT = "Helvetica"
    DEFAULT_FONT_SIZE = 8
    title= "Legend:"
        
        
    items_order = []
    items = {}
    
    color_loop = []
    color_curser = 0
    
    table=[]
    styles = []
    width = None
    
    
    def __init__(self, title=None):
        """ constructor """
        
        if title != None:
            self.title = title
        
        self.items_order = []
        self.items = {}
        
        self.color_loop = []
        self.color_curser = 0
        
        self.table = []
        self.styles = []
        
        self.width = 0

        #build a list of colors (picked up here: http://www.pagetutor.com/common/bgcolors1536.png )
        self.color_loop.append('#00ff66') #light green
        self.color_loop.append('#99ccff') #light blue
        self.color_loop.append('#ffaacc') #rose
        self.color_loop.append('#ffbb00') #orange
        self.color_loop.append('#ffff66') #yellow
        self.color_loop.append('#66cc55') #green
        self.color_loop.append('#0066ee') #blue
        self.color_loop.append('#cc99ff') #purple
        self.color_loop.append('#ff1133') #red
        self.color_loop.append('#cc8800') #braun
        self.color_loop.append('#cc4455') #dark red
        self.color_loop.append('#99aa11') #ugly green
        
        
    
        
    def add_item(self, label, color=None, id=None):
        """ create a new item and return it's id. 
            If the color is not defined, a color is defined automaticaly 
            If the id is not defined, an id is defined automaticaly
        """

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
        
        #color specified?
        if color != None:
            item_color = color
        else: 
            item_color = self.color_loop[self.color_curser]
            self.color_curser =  (self.color_curser + 1) % len(self.color_loop)
        
        #add the item 
        self.items_order.append(item_id)
        self.items[item_id] = ColorLegendItem(item_id, label, item_color)
        return item_id
        
        
    def add_unique_item(self, label, color=None, id=None):
        """ create an item only if the given label is not already used. 
            if the color is not defined, define one automaticaly
            return the id of the label (either the created one or the existing one )
        """
        
        item_exists = False
        for i in self.items: 
            if self.items[i].label == label:
                return self.items[i].id
        
        return self.add_item(label, color, id)
        
        
    def get_items_list(self):
        """ return the list of item and their associated color """
        
        result = []
        
        for i in self.items_order:
            result.append(self.items[i])
        
        return result
    
    
    def get_color(self, id):
        """ return the color code associated with an id """
        
        if id not in self.items_order:
            raise Exception("Id does not exist (id = %s). Be sure to add the item first with add_item() and retrieve its id from the return value" % id)
        
        return self.items[id].color
    
    
    def _build_table(self):
        """ return the list of list that represent the table structure """
        
        line = []
        if self.title != None:
            txt = c2c_helper.encode_entities(self.title)
            ps = ParagraphStyle('color_legend')
            ps.alignment = TA_CENTER
            ps.fontName = self.DEFAULT_FONT
            ps.fontSize = self.DEFAULT_FONT_SIZE
            p = Paragraph(txt, ps)        
            line.append([p])
            
        for i in self.items_order:
            line.append('')
        self.table.append(line)
        #global font for the whole graphic
        self.styles.append(('FONT', (0,0), (-1,-1),self.DEFAULT_FONT, self.DEFAULT_FONT_SIZE))
        # main frame arround the whole table
        self.styles.append(('BOX', (0,0), (-1,-1), 1, "#000000"))
        #in cells, text start in the top left corner
        self.styles.append(('VALIGN', (0,0), (-1,-1), 'TOP'))
        
        if self.title != None:
            #background of the legend title
            self.styles.append(('BACKGROUND', (0,0), (0,0), "#cccccc"))


    def _add_items(self):
        """ add labels and color to the table """
        
        #X starting position
        X_pos = 0 
        if self.title != None:
            X_pos = 1
        Y_pos = 0 
        
        cpt = 0
        for i in self.items_order:


            #add the label
            txt = c2c_helper.encode_entities(self.items[i].label)
            ps = ParagraphStyle('color_legend')
            ps.alignment = TA_CENTER
            ps.fontName = self.DEFAULT_FONT
            ps.fontSize = self.DEFAULT_FONT_SIZE
            p = Paragraph(txt, ps)            
            self.table[0][cpt+X_pos] = p
            
            #add the color
            self.styles.append(('BACKGROUND', (cpt+X_pos,0), (cpt+X_pos,0), self.items[i].color))
            cpt+=1
        
        


    def get_flowable(self, width):
        """ return the flowable object that can be insert into a template 
            "width" define the width of the whole legend table
        """
        
        self.width = width
        self._build_table()
        self._add_items()
                
        flowable = Table(self.table, self._compute_columns_widths(), repeatRows=0)
        flowable.setStyle(TableStyle(self.styles))
        return flowable


    def _compute_columns_widths(self):
        """construct the list of column widths. """
        
        columns_width = []
        if self.title != None:
            title_length = stringWidth(self.title, self.DEFAULT_FONT, self.DEFAULT_FONT_SIZE)+10 #add 10 to include margins
            columns_width.append(title_length)
            
        total_width = self.width-title_length
        if len(self.items_order):
            columns_width += len(self.items_order) * [total_width / len(self.items_order)]
        else:
            columns_width = total_width
        return columns_width
       
       

#       this commmented stuff below is another way to compute the legend'cells width proportionately to the content's length.
############################################################################################################################
#
#        #to build a beautiful legend on one line, I compute all text length and then define a ratio for each columns.
#        #so long texts will have more room than short ones
#        total_width = 0
#
#        #include the title to the calculation
#        title_length = 0
#        
#        for i in self.items_order:
#            string_width = stringWidth(self.items[i].label, self.DEFAULT_FONT, self.DEFAULT_FONT_SIZE)
#            self.items[i].string_width = string_width
#            total_width += string_width
#        
#        #compute the ratio
#        ratio = (self.width -title_length) / total_width
#        #apply the ratio to each element
#        columns_width = []
#        
#        if self.title != None:
#            columns_width.append(title_length)
#        
#        for i in self.items_order:
#            columns_width.append(ratio * self.items[i].string_width)
#        return columns_width
    
        


class ColorLegendItem(object):
    """this class represent an item of the color legend"""
    color = None
    label = None
    id = None
    string_width = None
    
    def __init__(self, id, label, color):
        """ constructor """
        self.color = color
        self.label = label
        self.id = id
        self.string_width = 0




class ColorLegendTable(Table):
    """ the flowable object returned by ColorLegendBuilder->get_flowable() """
    
    def draw(self):
        """ called by the template engine to ask the table to draw itself"""
                
        Table.draw(self)
        
        