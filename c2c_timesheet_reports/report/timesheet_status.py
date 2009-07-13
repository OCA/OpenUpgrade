# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) Camptocamp SA
# Author: Arnaud Wüst
#
#
#    This file is part of the c2c_timesheet_report module
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

import time
from report import report_sxw
import pooler
from mx import DateTime
import netsvc



class timesheet_status(report_sxw.rml_parse):
    
    _name = 'c2c_timesheet_reports.timesheet_status'
    
    
    cr = None
    pool = None
    uid = []
    context = {}
    data = {}
    

    def __init__(self, cr, uid, name, context):
        """ init """
        
        super(timesheet_status, self).__init__(cr, uid, name, context)
        self.logger = netsvc.Logger()

        self.data = {}
        self.time = time.time()        
        self.cr = cr
        self.pool = pooler.get_pool(self.cr.dbname)
        self.uid = uid
        self.context = context
        
        self.localcontext.update({
            'compute': self.compute,
            'time': time,
            'get_title': self.get_title,
            
            'get_timerange_title': self.get_timerange_title,
            'get_user_list': self.get_user_list,
            'get_timesheet_status': self.get_timesheet_status,           
        })
        
        
    
    def compute(self, objects, data):
        """compute all datas and do all the calculations before to start the rml rendering 
           - objects are companies
           - data is a dictionnary from the form
        """        
        
        #init the data array
        for o in objects:
            self.data[o.id] = {}
        
        #get the list of employees ids to treat
        for o in objects:                
            self.data[o.id]['employees'] = self._compute_employees_list(o)
        
        #get the time range for each company
        for o in objects:
            self.data[o.id]['time_ranges'] = self._compute_periods(o, time.strptime(data['form']['date'], "%Y-%m-%d"))
            
        #get the status of each timesheet for each employee
        for o in objects:
            
            self.data[o.id]['sheet_status'] = self._compute_all_status(o)
        
                
    
    def _compute_employees_list(self, company):
        """ return a dictionnary of lists of employees ids linked to the companies (param company) """        
        return self.pool.get('c2c_timesheet_reports.reminder').compute_employees_list(self.cr, self.uid, self.context, company)


    def _get_last_period_dates(self, company, date):
        """ return the start date of the last period to display """
        return self.pool.get('c2c_timesheet_reports.reminder').get_last_period_dates(company, date)
        
    
    def _compute_periods(self, company, date):
        """ return the timeranges to display. This is the 5 last timesheets (depending on the timerange defined for the company) """
        return self.pool.get('c2c_timesheet_reports.reminder').compute_periods(company, date)


    
    def get_title(self, obj):
        """ return the title of the main table """


        last_id = len(self.data[obj.id]['time_ranges']) -1
        start_date = time.strptime(str(self.data[obj.id]['time_ranges'][last_id][0]), "%Y-%m-%d %H:%M:%S.00")
        start_date = time.strftime("%d.%m.%Y",start_date)
        
        end_date = time.strptime(str(self.data[obj.id]['time_ranges'][0][1]), "%Y-%m-%d %H:%M:%S.00")
        end_date = time.strftime("%d.%m.%Y",end_date)

        
        return obj.name+", "+start_date+" to "+end_date
    
    def get_timerange_title(self, obj, cpt):
        """ return a header text for a periods column """
        start_date = self.data[obj.id]['time_ranges'][cpt][0]       
        start_date = time.strptime(str(start_date), "%Y-%m-%d %H:%M:%S.00")
        start_date = time.strftime("%d.%m.%Y",start_date)
        
        end_date = self.data[obj.id]['time_ranges'][cpt][1]       
        end_date = time.strptime(str(end_date), "%Y-%m-%d %H:%M:%S.00")
        end_date = time.strftime("%d.%m.%Y",end_date)

        return start_date+"\n "+end_date


    def get_user_list(self, obj):
        """ return the list of employees object ordered by name """
        return self.data[obj.id]['employees']
    
    
    def get_timesheet_status(self, obj, user, cpt):
        """ return the status to display for a user and a period """

        #find the parent blockTable
        para = self._find_parent(self._node, 'para')
        #set the attribut to the blockTable
        
        para.setAttribute('style', self.data[obj.id]['sheet_status'][cpt][user.id])
        
        return self.data[obj.id]['sheet_status'][cpt][user.id]
   

   
    def _compute_timesheet_status(self, obj, employee, period):
        """ return the timesheet status for a user and a period """
        return self.pool.get('c2c_timesheet_reports.reminder').compute_timesheet_status(self.cr, self.uid, self.context, obj, employee, period)

                    
    def _compute_all_status(self, o):
        """ compute all status for all employees for all periods """
        result = {}
        
        #for each periods
        for p_index in range(len(self.data[o.id]['time_ranges'])):
            result[p_index] = {}
            p = self.data[o.id]['time_ranges'][p_index]
            #for each employees
            for e in self.data[o.id]['employees']:
                
                #compute the status
                result[p_index][e.id] = self._compute_timesheet_status(o, e, p)
        
        return result            
                    
report_sxw.report_sxw('report.c2c_timesheet_reports.timesheet_status', 'res.company', 'c2c_timesheet_reports/report/timesheet_status.rml', parser=timesheet_status, header=False)