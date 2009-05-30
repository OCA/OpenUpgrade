# -*- coding: utf-8 -*- 
##############################################################################
#
# Copyright (c) Camptocamp SA - http://www.camptocamp.com
# Author: Arnaud Wüst
#
#    This file is part of the c2c_reporting_tools module
#    This file contain: 
#    - PythonReport. The class to extend in order to create a new Python report
#    - StandardReport. The class to extend in order to create an internal standard report
#
#    To use StandardReport, extend the class and redefine the method get_story to return an array of flowables. 
#
#            HELLO WORLD EXEMPLE: 
#        
#            from c2c_reporting_tools.reports.standard_report import StandardReport
#            from reportlab.platypus import Paragraph
#            from reportlab.lib.styles import ParagraphStyle
#            
#            class myReport(StandardReport):  
#                
#                def get_story(self):
#                    """ """
#                    return [Paragraph("Hello World",ParagraphStyle("dummy"))]
#                       
#            myReport('report.my_module.my_report', "My First Report", myReport.A4_LANDSCAPE)        

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
from report.interface import report_int

from c2c_reporting_tools import *

from c2c_reporting_tools.templates.standard_template import *
from c2c_reporting_tools.translation import _


import pooler
import netsvc
import time

import tools
import inspect


class PythonReport(report_int): 
    """ report made in python """

    logger = None

    cr = None
    uid = None
    ids = None
    datas = None
    context = None
    pool = None
    objects_name = None
    objects = None
    width= None
    lang = None
    
    def __init__(self, openerp_name, objects_name=None):
        """ constructor """
        self.logger = netsvc.Logger()
        self.objects_name = objects_name
        super(PythonReport, self).__init__(openerp_name)
        
            
    def get_template(self, cr, context):
        """ define the template of the report """
        raise Exception('You must override this method python_report.get_template (and not call the parent) to define the report\'s template')
   
        
    def get_story(self):
        """ define the content of the report. """
        raise Exception('You must override this method python_report.get_story (and not call the parent) to define the report\'s story')
        
        
    def create(self, cr, uid, ids, datas, context={}):
        """ construct the report """

        #init
        self.cr = cr
        self.uid= uid
        self.datas = datas
        self.context = context              
        self.pool = pooler.get_pool(self.cr.dbname)
        self.lang = context.get('lang', None)
        
        #lines ids come from a wizard form
        if 'form' in self.datas and 'ids' in self.datas['form']:
            self.ids = self.datas['form']['ids']
        #lines ids come from the line selection
        else:
            self.ids = ids            

        
        #get objects
        if self.objects_name:
            self.objects = pooler.get_pool(self.cr.dbname).get(self.objects_name).browse(self.cr, self.uid, self.ids)
        
        
        #template
        doc = self.get_template(cr, context)
        self.width = doc.get_content_width()
        #content 
        story = self.get_story()
                        
        return doc.fillWith(story)
        
        
    def _(self, source):
        """ 
            Handle translations. 
            Because cr and context['lang'] are not available in local context (but in object properties) you can not use c2c_reporting_tools.translation._() in reports
            Use self._() insead
        """
        frame = inspect.stack()[1][0]        
        filename= frame.f_code.co_filename
        result = tools.translate(self.cr, self.uid, filename, 'code', self.lang, source) or source 
        return result


class StandardReport(PythonReport):
    
    #available templates' names
    A4_PORTRAIT = "A4_PORTRAIT"
    A4_PORTRAIT_WO_TOTPAGE = "A4_PORTRAIT_WO_TOTPAGE"
    A4_LANDSCAPE = "A4_LANDSCAPE"
    A4_LANDSCAPE_WO_TOTPAGE = "A4_LANDSCAPE_WO_TOTPAGE"
    
    template_name = None
    
    def __init__(self, openerp_name, title="", objects_name=None, template_name=None):
        """ DO NOT USE title PARAM anymore. Overload get_template_title() instead """
        
        self.template_name = template_name        
        self.template_title = title
            
        super(StandardReport, self).__init__(openerp_name, objects_name)
           
    def get_template(self, cr, context):
        """ define the template of the report """

        # choose the appropriate template
        if self.template_name == self.A4_LANDSCAPE:
            doc = STLandscapeTotalPage()
        elif self.template_name == self.A4_LANDSCAPE_WO_TOTPAGE:
            doc = STLandscape()
        elif self.template_name == self.A4_PORTRAIT_WO_TOTPAGE:
            doc = STPortrait()
        else:
            doc = STPortraitTotalPage()

            
        user = self.pool.get('res.users').browse(self.cr,self.uid,self.uid, self.context)        
        doc.company_name = user.company_id.name
            
            
        doc.report_name = self.get_template_title(cr, context)
        
        return doc
    
    def get_template_title(self, cr, context):
        """return the default title of the template. Overload the method to redefine and translate the title"""
        
        return self.template_title

        