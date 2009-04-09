# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) Camptocamp SA
# Author: Arnaud Wüst
#
#
#    This file is part of the c2c_report_tools module.
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
from osv import osv

import time
import datetime
from datetime import timedelta
import os.path
import tools
import re


class c2c_helper(osv.osv):
    """ a class that provide useful methods for template development """
    
    # format of the dates
    timeformat = " %d.%m.%y"


    @staticmethod
    def unique(seq, keepstr=True):
        """return a list whithout duplicated elements 
           found here: http://groups.google.com/group/comp.lang.python/msg/7b0d896a96d907f3
        """
        t = type(seq)
        if t==str:
            t = (list, ''.join)[bool(keepstr)]
        seen = []
        return t(c for c in seq if not (c in seen or seen.append(c)))


    @staticmethod
    def comma_me(amount, decimals=2, separator="'"):
        """ transform a number into a number with thousand separators """
        if type(amount) is int: 
            amount = str(('%.'+str(decimals)+'f')%float(amount))
        elif  type(amount) is float :
            amount = str(('%.'+str(decimals)+'f')%amount)
        else :
            amount = str(amount)
        orig = amount
        new = re.sub("^(-?\d+)(\d{3})", "\g<1>"+separator+"\g<2>", amount)
        if orig == new:
            return new
        else:
            return c2c_helper.comma_me(new)

        
    @staticmethod
    def format_date(date, timeformat=None):
        """transform an english formated date into a swiss formated date (the format define is define as a class constant c2c_helper.timeformat """
        if timeformat == None:
            timeformat = c2c_helper.timeformat
        if date:
            return time.strftime(timeformat, time.strptime(date, "%Y-%m-%d"))
        return None
    
    
    @staticmethod
    def parse_datetime(datetime):
        """parse an openerp datetime value and return a python time struct """
        return time.strptime(datetime, "%Y-%m-%d %H:%M:%S")
        
    @staticmethod
    def parse_date(date):
        """parse an openerp date value and return a python time struct """
        return time.strptime(date, "%Y-%m-%d")
    
    
    @staticmethod
    def encode_entities(s):
        """replace template knotty symbols by their html code"""
            
        s = s.replace('&', '&amp;')
        
        #an opening symbol without a closing symbol would crash the server...
        if s.count('>') != s.count('<'):
            s= s.replace('<', '&#60;')
            s= s.replace('>', '&#62;')
        
        return s
        
    
    @staticmethod
    def ellipsis(string, maxlen=100, ellipsis = '...'):
        """cut a string if its length is greater than maxlen and add ellipsis (...) after """
        ellipsis = ellipsis or ''
        if len(string) > maxlen:
             #the string must be cutted
            result = string[:maxlen - len(ellipsis) ] + (ellipsis, '')[len(string) < maxlen]
        else: 
            result = string
        return result
    
    
    @staticmethod    
    def exchange_currency(cr, amount, from_currency_id, to_currency_id, date=None):
        """ exchange an amount from a currency to another.
            date format: python struct_time returned by gmtime()
        """
        
        if amount == 0:
            return 0
        
        #no need to compute anything if we do not need to exchange the amount
        if from_currency_id == to_currency_id:
            return amount
        
        if from_currency_id == None or to_currency_id == None:
            raise osv.except_osv('Param Errors', 'Currencies can not be None')
            
        #default date
        if not date:
            date = time.gmtime(time.time())
        
        #format the date for the sql
        date_sql = time.strftime("%Y-%m-%d", date)
        
        currencies_sql = ",".join(map(str,[from_currency_id, to_currency_id]))
        
        
        #get all the rates defines for the two currencies
        query = '''SELECT currency_id, rate, name 
                   FROM res_currency_rate 
                   WHERE currency_id IN (%s) 
                   AND name <= '%s'
                   ORDER BY name ASC ''' % (currencies_sql, date_sql)
        cr.execute(query)
        rates_db = cr.fetchall()
        
        rates = {}
        #update the currencies rate until the rate's date is greater than the given one
        #in order to get the last rate defined before the date
        for rate in rates_db:
            if time.strptime(rate[2], "%Y-%m-%d") <= date:
                rates[rate[0]] = rate[1]
                
        
        #exchange
        result = False
        if from_currency_id in rates and to_currency_id in rates:
            result = amount * rates[to_currency_id]  / rates[from_currency_id] 

        return result

    
    @staticmethod
    def week_first_day(date):
        """ return the date of the first day of the week concerned by the given date 
            'date' is a datetime
        """
        
        
        if date.weekday() == 0: #monday
            return date
        
        return  date - timedelta(days=date.weekday())
   
    
    @staticmethod
    def week_last_day(date):
        """ return the date of the last day of the week concerned by the given date 
            last_day_name can be "saturday" or "sunday"
            'date' is a datetime
        """
        
        if date.weekday() == 6: #sunday
            return date
        
        return date + timedelta(days=6-date.weekday())



    @staticmethod
    def month_first_day(dt, d_years=0, d_months=0):
        """
        return the first day of the month concerned by the given date (param dt)
        ignore otional params, there are just here to be used by c2c_helper.last_day_of_the_month
        found here: http://code.activestate.com/recipes/476197/
        """

        #convert the param to a datetime for processing
        my_date = dt
        if isinstance(dt,time.struct_time):
            my_date = datetime.datetime(*dt[:6])
        
        
        # d_years, d_months are "deltas" to apply to dt
        y, m = my_date.year + d_years, my_date.month + d_months
        a, m = divmod(m-1, 12)
        
        
        res = datetime.datetime(y+a, m+1, 1,0,0,0)
        
        #return a struct_time if the param was a struct_time
        if isinstance(dt, time.struct_time):
            res = res.timetuple()
    
        return res
       
       
    @staticmethod
    def month_last_day(dt):
        """
        return the last day of the month
        found here: http://code.activestate.com/recipes/476197/
        """

        my_date = dt
        if isinstance(dt,time.struct_time):
            my_date = datetime.datetime(*dt[:6])
        
        res = c2c_helper.month_first_day(my_date, 0, 1) + datetime.timedelta(-1)
        
        if isinstance(dt,time.struct_time):
            res = res.timetuple()
        
        return res
    
        