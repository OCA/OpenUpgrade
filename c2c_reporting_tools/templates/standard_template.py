# -*- coding: utf-8 -*- 
##############################################################################
#
# Copyright (c) Camptocamp SA - http://www.camptocamp.com
# Author: Arnaud Wüst
#
#    This file is part of the c2c_report_tools templates
#    It contains the following classes:
#    - STPortrait: A basic A4 template for internal reports. header with company name and report name.  footer with date and page number. Portrait orientation.
#    - STLandscape: Identical to STPortrait but Landcape orientation.
#    - STPortraitTotalPage: Identical to STPortrait but add the total number of pages beside the page number. (Require more processing)
#    - STLandscapeTotalPage Identical to STPortrait but landscape orientation and total page number in the footer
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
from reportlab.platypus import BaseDocTemplate, PageTemplate
from reportlab.lib.units import mm
import StringIO
import time
import pooler
from datetime import datetime, timedelta

    
class STPortrait(BaseDocTemplate):
    ''' "ST" stands for "Standard Template"
        the standard OpenErp internal template with a header that contain just the company name and the report name
        and a footer that contain the print date and the page numbers '''
       
    company_name = ""
    report_name= ""  
    footer_time = 0
    
    #dimentions
    PAGE_HEIGHT = 297 * mm
    PAGE_WIDTH = 210 * mm
    
    LEFT_MARGIN = 5 * mm
    RIGHT_MARGIN = 5 * mm
    TOP_MARGIN = 5 * mm
    BOTTOM_MARGIN = 5 * mm
    
    HEADER_HEIGHT = 10 * mm
    FOOTER_HEIGHT = 7 * mm
    
    #filename used to generate the pdf content and retrieve it
    io = None
        
    def __init__(self, **kw):
        self.io = StringIO.StringIO()
        self.footer_time = time.strftime("%m-%d-%y %H:%M", time.localtime())    
        apply(BaseDocTemplate.__init__,(self,self.io),kw)

        
    def get_header_left_pos(self):
        '''return the Y coordinate of header's left border '''
        return self.LEFT_MARGIN
    def get_header_right_pos(self):
        '''return the Y coordinate of the header's right border '''
        return self.PAGE_WIDTH - self.RIGHT_MARGIN
    def get_header_top_pos(self):
        '''return the X coordinate of the header's top border'''
        return self.PAGE_HEIGHT - self.TOP_MARGIN
    def get_header_bottom_pos(self):
        '''return the X coordinate of the header's bottom border'''
        return self.PAGE_HEIGHT - self.TOP_MARGIN - self.HEADER_HEIGHT    
    def get_content_left_pos(self):
        '''return the X coordinate of the content's left border '''
        return self.LEFT_MARGIN
    def get_content_right_pos(self):
        '''return the X coordinate of the content's right border '''
        return self.PAGE_WIDTH - self.RIGHT_MARGIN
    def get_content_top_pos(self):
        '''return the Y coordinate of the content's top border '''
        return self.PAGE_HEIGHT - self.TOP_MARGIN - self.HEADER_HEIGHT
    def get_content_bottom_pos(self):
        '''return the Y coordinate of the content's bottom border '''
        return self.BOTTOM_MARGIN + self.FOOTER_HEIGHT
    def get_content_height(self):
        '''return the height of the content zone'''
        return self.PAGE_HEIGHT - (self.TOP_MARGIN + self.BOTTOM_MARGIN + self.HEADER_HEIGHT + self.FOOTER_HEIGHT)
    def get_content_width(self):
        '''return the width of the content zone'''
        return self.PAGE_WIDTH - (self.LEFT_MARGIN + self.RIGHT_MARGIN)
    def get_footer_left_pos(self):
        '''return the Y coordinate of footer's left border '''
        return self.LEFT_MARGIN
    def get_footer_right_pos(self):
        '''return the Y coordinate of the footer's right border '''
        return self.PAGE_WIDTH - self.RIGHT_MARGIN
    def get_footer_top_pos(self):
        '''return the X coordinate of the footer's top border'''
        return self.BOTTOM_MARGIN + self.FOOTER_HEIGHT
    def get_footer_bottom_pos(self):
        '''return the X coordinate of the footer's bottom border'''
        return self.BOTTOM_MARGIN


    
    def _drawPageTemplate(self, c, doc):
        '''draw the standard header and the footer. c is the canvas'''
        
        c.saveState()
        
        c.setFont('Helvetica-Bold', 8)
        #draw the header text (company name and report name)
        header_text_height = self.get_header_bottom_pos() + 7*mm
        c.drawString(self.get_header_left_pos(), header_text_height, self.company_name)
        c.drawRightString(self.get_header_right_pos(), header_text_height, self.report_name)
        
        #draw the header line
        header_line_height = self.get_header_bottom_pos() + 5*mm
        c.line(self.get_header_left_pos(), header_line_height, self.get_header_right_pos(), header_line_height)    
        
        #draw the footer line
        footer_line_height = self.get_footer_top_pos() - 2*mm
        c.line(self.get_footer_left_pos(), footer_line_height, self.get_footer_right_pos(), footer_line_height)
                
        #draw the date and the page number
        c= self._drawFooterText(c)
        
        c.restoreState()
    
    def _drawFooterText(self, c):
        ''' draw the footer text. Called by _drawPageTemplate '''
        footer_text_height = self.get_footer_top_pos() - 7*mm
        c.drawString(self.get_footer_left_pos(),footer_text_height, self.footer_time)
        c.drawRightString(self.get_footer_right_pos(), footer_text_height,  "Page %s" % (c.getPageNumber()) )
        return c
        
    def _callParentBuild(self, story):
        """call the parent build method (sparated in a method to allow children classes to redefine it and call multibuild if needed) """
        BaseDocTemplate.build(self, story)
        
    def fillWith(self, story):
        '''this template with the content given in story. Then return the pdf content as it must be returned by the method "create" of the report object'''
        self._calc()
        
        # only one frame in one template
        frame = platypus.Frame(self.get_content_left_pos(), self.get_content_bottom_pos(), self.get_content_width(), self.get_content_height(), 0, 0, 0, 0, id='mainFrame')
        template = PageTemplate('mainTemplate', [frame], lambda c,doc:self._drawPageTemplate(c, doc), pagesize=(self.PAGE_WIDTH, self.PAGE_HEIGHT))
        self.addPageTemplates(template)   
        self._callParentBuild(story)
        return (self.io.getvalue(), 'pdf')


class STLandscape(STPortrait):
    ''' ST stands for "Standard Template" 
        Idem as STPortrait but for landscape format
    '''
    PAGE_HEIGHT = 210 * mm
    PAGE_WIDTH = 297 * mm


class STPortraitTotalPage(STPortrait):
    ''' ST stands for "Standard Template" 
        Idem as STPortrait but add the total page number at the bottom of the page
        
        Warning: It require more processing than STPortrait because all drawings are made twice
    '''

    numPages = 1
    
    def progresshandler(self, what, arg):
        """ receive messages on each step of the template processing"""
        if what=='STARTED':
            self._lastnumPages = self.numPages          
        #print what, arg

    def _allSatisfied(self):
        """ multibuild ask this method to know if a additionnal pass is requiered. If return 0, a new pass is run"""
        if self._lastnumPages < self.numPages:
            return 0
        return BaseDocTemplate._allSatisfied(self)

                
    def afterInit(self):
        """ This is called after the initialisation, for each pass"""
        self.numPages = 1
        self._lastnumPages = 0
        self.setProgressCallBack(self.progresshandler)


    def afterPage(self):
        """This is called after page processing, and
        immediately after the afterDrawPage method
        of the current page template."""
        self.numPages = max(self.canv.getPageNumber(), self.numPages)
    
    
    def _drawFooterText(self, c):
        ''' draw the footer text. Called by _drawPageTemplate '''
        footer_text_height = self.get_footer_top_pos() - 7*mm
        c.drawString(self.get_footer_left_pos(),footer_text_height, self.footer_time)
        c.drawRightString(self.get_footer_right_pos(), footer_text_height,  "Page %s / %s" % (c.getPageNumber(), self.numPages) )
        return c

    def _callParentBuild(self, story):
        """ call the parent multibuild. to pass the drawing more than once """
        BaseDocTemplate.multiBuild(self, story)
 

class STLandscapeTotalPage(STPortraitTotalPage):
    ''' ST stands for "Standard Template" 
        Idem as STPortraitTotalPage but for landscape format

        Warning: It require more processing than STLandscape because all drawings are made twice    
    '''
    PAGE_HEIGHT = 210 * mm
    PAGE_WIDTH = 297 * mm
       
