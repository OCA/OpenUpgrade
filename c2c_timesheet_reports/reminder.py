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

from c2c_reporting_tools.translation import _

from osv import fields, osv
import time
from datetime import datetime, timedelta
from mx import DateTime
import pooler
import tools


class reminder (osv.osv):
    _name = "c2c_timesheet_reports.reminder"
    _description = "Handle the scheduling of messages"
    
    
    _columns  = {
            'reply_to' : fields.char('Reply To', size=100),
            'message'  : fields.text('Message'),
            'subject'  : fields.char('Subject', size=200),
    }
        
      
    #default cron (the one created if missing)
    cron = {'active'          : False,
            'priority'        : 1,
            'interval_number' : 1,
            'interval_type'   : 'weeks',
            'nextcall'        : time.strftime("%Y-%m-%d %H:%M:%S", (datetime.today() + timedelta(days=1)).timetuple() ), #tomorrow same time
            'numbercall'      : -1,
            'doall'           : True,
            'model'           : 'c2c_timesheet_reports.reminder',
            'function'        : 'run',
            'args'            : '()',
            }
    
    #default message (the one created if missing)
    message = {'reply_to': 'spam@camptocamp.com'
              }
        
    
    
    def run(self, cr, uid):
        """ find the reminder recipients and send them an email """
        
        #get all companies
        companies = self.pool.get('res.company').browse(cr, uid, self.pool.get('res.company').search(cr, uid, []))
        
        #for each company, get all recipients
        recipients = []
        for c in companies: 
            recipients += self.get_recipients(cr, uid, {}, c) 
        
        #get the message to send
        message_id = self.get_message_id(cr, uid, {})
        message_data = self.browse(cr, uid, message_id)
        
        
        #send them email if they have an email defined
        emails = []
        for r in recipients:

            if r.work_email:
                emails.append(r.work_email)
        if emails :
            tools.email_send(message_data.reply_to, [], message_data.subject, message_data.message, email_bcc=emails)
            
            
        
                
    def get_recipients(self, cr, uid, context, company):
        """return the list of users that must recieve the email """
        
        #get the whole list of employees
        employees = self.compute_employees_list(cr, uid, context, company)
        
        #periods
        periods = self.compute_periods(company, time.gmtime(), 13)
        #remove the first one because it's the current one
        del periods[0]
        

        recipients = []

        # for each employee
        for e in employees:
            

            #if the user still in the company? 
            in_company = True
            if (e.started != False and e.started > time.strftime('%Y-%m-%d') ) or (e.ended != False and e.ended < time.strftime('%Y-%m-%d') ):
                #do nothing... this user is not concerned anymore by timesheets
                pass
            else:
                #and for each periods
                for p_index in range(len(periods)):
                    p = periods[p_index]
                    status = self.compute_timesheet_status(cr, uid, context, company, e, p)
                    
                    # if there is a missing sheet or a draft sheet
                    # and the user can receive alerts
                    #then  we must alert the user
                    if status in ['Missing', 'Draft'] and e.receive_timesheet_alerts :
                        recipients.append(e)
                        break # no need to go further for this user, he is now added in the list, go to the next one
                
        return recipients
                
               
                
        
    def compute_periods(self, company, date, periods_number=5):
        """ return the timeranges to display. This is the 5 last timesheets (depending on the timerange defined for the company) """
        
        periods = []
        
        (last_start_date, last_end_date) = self.get_last_period_dates( company, date)
        
        for cpt in range(periods_number):
            #find the delta between last_XXX_date to XXX_date
            if company.timesheet_range == 'month':
                delta = DateTime.RelativeDateTime(months=-cpt)
            elif company.timesheet_range == 'week':
                delta = DateTime.RelativeDateTime(weeks=-cpt)
            elif company.timesheet_range == 'year':
                delta = DateTime.RelativeDateTime(years=-cpt)
            
            start_date = last_start_date + delta
            end_date  = last_end_date   + delta
            periods.append( (start_date, end_date) )
            
        return periods
                    

    def get_last_period_dates(self, company, date):
        """ return the start date and end date of the last period to display """
        
        # return the first day and last day of the month 
        if company.timesheet_range == 'month':
            start_date = DateTime.Date(date.tm_year, date.tm_mon, 1)
            end_date = start_date + DateTime.RelativeDateTime(months=+1)
        #return the first and last days of the week
        elif company.timesheet_range == 'week':
            start_date = DateTime.Date(date.tm_year, date.tm_mon, date.tm_mday) + DateTime.RelativeDateTime(weekday=(DateTime.Monday,0))
            end_date = DateTime.Date(date.tm_year, date.tm_mon, date.tm_mday) + DateTime.RelativeDateTime(weekday=(DateTime.Sunday,0))
        # return the first and last days of the year
        elif company.timesheet_range == 'year':
            start_date = DateTime.Date(date.tm_year, 1, 1)
            end_date = DateTime.Date(date.tm_year, 12, 31)
            
        return (start_date, end_date)


    def compute_employees_list(self, cr, uid, context, company):
        """ return a dictionnary of lists of employees ids linked to the companies (param company) """
        hr_employee_object = self.pool.get('hr.employee')
        
        employees = []


        #employees associated with a Tinyerp user
        users_ids = self.pool.get('res.users').search(cr, uid, [('company_id', '=', company.id)], context=context)
        employees_users_ids = hr_employee_object.search(cr, uid, [('user_id', 'in', users_ids)])
        
        #combine the two employees list, remove duplicates and order by name DESC
        employees_ids = hr_employee_object.search(cr, uid, [('id', 'in', employees_users_ids)], order="name ASC", context=context)
            
        return hr_employee_object.browse(cr, uid, employees_ids, context=context)        
    
    
    
   
    def compute_timesheet_status(self, cr, uid, context, obj, employee, period):
        """ return the timesheet status for a user and a period """
        
        status = 'Error'
        
        time_from = time.strptime(str(period[0]),"%Y-%m-%d %H:%M:%S.00")
        time_to = time.strptime(str(period[1]), "%Y-%m-%d %H:%M:%S.00")
                
        #if the starting date is defined and is greater than the date_to, it means the employee wasn't one at this period
        if employee.started != None and (employee.started != False) and time.strptime(employee.started,"%Y-%m-%d") > time_to:
            status = 'Not in Company'
        #if the ending date is defined and is earlier than the date_from, it means the employee wasn't one at this period
        elif employee.ended != None and (employee.ended != False) and time.strptime(employee.ended, "%Y-%m-%d") < time_from:
            status = 'Not in Company'
        #the employee was in the company at this period
        else:

    
            # does the timesheet exsists in db and what is its status?
            timeformat = "%Y-%m-%d"
            date_from = time.strftime(timeformat, time_from  )
            date_to =   time.strftime(timeformat, time_to ) 
            
            
            sheet = []
            if employee.user_id.id != False:
                query = """SELECT state, date_from, date_to FROM hr_timesheet_sheet_sheet 
                           WHERE user_id = %s 
                           AND date_from >= '%s'
                           AND date_to <= '%s'
                        """ % (employee.user_id.id, date_from, date_to)
                cr.execute(query)
                sheets = cr.dictfetchall()
            
                #the tiemsheet does not exists in db
                if len(sheets) == 0:
                    status = 'Missing'
                
                if len(sheets) > 0:
                    status = 'Confirmed'
                    for s in sheets:
                        if s['state'] == 'draft':
                            status = 'Draft'
        return status
    
    
    
    
    def get_cron_id(self, cr, uid, context):
        """return the reminder cron's id. Create one if the cron does not exists """
        
        cron_id = 0
        cron_obj = self.pool.get('ir.cron')
        try: 
            #find the cron that send messages
            cron_id = cron_obj.search(cr, uid,  [('function', 'ilike', self.cron['function']), ('model', 'ilike', self.cron['model'])], context={'active_test': False} )
            cron_id = int(cron_id[0])
        except Exception,e :
            print e
            print 'warning cron not found one will be created'
            pass # ignore if the cron is missing cause we are going to create it in db
        
        #the cron does not exists
        if not cron_id :
            #translate
            self.cron['name'] = _('timesheet status reminder')
            cron_id = cron_obj.create(cr, uid, self.cron, context)
        
        return cron_id
    
    
    
    
    def get_message_id(self, cr, uid, context):
        """ return the message'id. create one if the message does not exists """
        message_id = 0
        
        try: 
            #there is only one line in db, let's get it
            message_id = int(self.search(cr, uid, [], offset=0, limit=1, context=context)[0])
        except Exception:
            #"unable to find the message". I ignore this error and try to create the message if it does not exists
            pass
    
        #the message does not exists
        if message_id == 0:
            #translate
            self.message['subject'] = _('Timesheet Reminder')
            self.message['message'] = _('At least one of your last timesheets is still in draft or is missing. Please take time to complete and confirm it.')
            
            message_id = self.create(cr, uid, self.message, context)
            
        return message_id
            
            
            
    def get_config(self, cr, uid, context):
        """return the reminder config from the db """
        
        cron_id = self.get_cron_id(cr, uid, context)
        
        cron_data = self.pool.get('ir.cron').browse(cr, uid, cron_id)
                
        #there is only one line in db, let's get it
        message_id = self.get_message_id(cr, uid, context)
        message_data = self.browse(cr, uid, message_id)
        return { 'reminder_active': cron_data.active , 
                 'interval_type': cron_data.interval_type, 
                 'interval_number': cron_data.interval_number, 
                 'reply_to': message_data.reply_to, 
                 'message':  message_data.message , 
                 'subject': message_data.subject,
                 'nextcall': cron_data.nextcall,
               }        
        
        
    
    def save_config(self, cr, uid, datas, context):
        """save the reminder config """
        #modify the cron
        cron_id = self.get_cron_id(cr, uid, context)        
        result = self.pool.get('ir.cron').write(cr, uid, [cron_id], {'active': datas['reminder_active'],
                                                           'interval_number' : datas['interval_number'],
                                                           'interval_type'   : datas['interval_type'],
                                                           'nextcall'        : datas['nextcall'],
                                                                })    
        #modify the message
        message_id = self.get_message_id(cr, uid, context)
        result = self.write(cr, uid, [message_id], {'reply_to': datas['reply_to'],
                                                    'message': datas['message'],  
                                                    'subject': datas['subject'],
                                                   })
    
        #et pour finir, fait un petit tour de passe passe, huhuhu
        pass
        pass
    
        
        #return an empty dictionnary because actions method must do so...
        return {}
        
    
reminder()    