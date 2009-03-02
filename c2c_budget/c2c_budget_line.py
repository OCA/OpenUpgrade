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

from osv import fields, osv
from c2c_reporting_tools.c2c_helper import *   
from datetime import datetime
from time import mktime
import time


class c2c_budget_line(osv.osv):
    """ camptocamp budget line. A budget version line NOT linked to an analytic account """
    
    
    def filter_by_period(self, cr, uid, lines, periods_ids, context={}):
        """ return a list of lines amoungs those given in parameter that are linked to one of the given periods """
        result = []
        
        if len(periods_ids) == 0:
            return []
        
        for l in lines:
            if l.period_id.id in periods_ids: 
                result.append(l) 
                   
        return result

    
    
    def filter_by_date(self, cr, uid, lines, date_start=None, date_end=None, context={}):
        """return a list of lines among those given in parameter that stand between date_start and date_end """
        result = []
        
        for l in lines:
            if (date_start == None or l.period_id.date_start >= date_start) and (date_end == None or l.period_id.date_stop <= date_end):
                result.append(l) 
                   
        return result
    
    
    
    def filter_by_missing_analytic_account(self, cr, uid, lines, context={}):
        """return a list of lines among those given in parameter that are ot linked to a analytic account """
        result = []
        
        for l in lines:
            if not l.analytic_account_id:
                result.append(l) 
                
        return result
    
    
        
    def filter_by_items(self, cr, uid, lines, items_ids, context={}):
        """return a list of lines among those given in parameter that are linked to one of the given items """
        result = []
        
        budget_items_obj = self.pool.get('c2c_budget.item')        
        all_items = budget_items_obj.get_sub_items(cr, items_ids)

        for l in lines:
            if l.budget_item_id.id in all_items:
                result.append(l)
                
        return result
    
    
    
    def filter_by_analytic_account(self, cr, uid, lines, analytic_accounts_ids, context={}):
        """return a list of lines among those given in parameter that is linked to analytic_accounts.
            param analytic_accounts_ids should be a list of accounts'ids. """
        result = []
        
        aa_obj = self.pool.get('account.analytic.account')
        all_accounts = aa_obj.get_children_flat_list(cr, uid, analytic_accounts_ids)
        
        for l in lines:
            if l.analytic_account_id.id in all_accounts:
                result.append(l) 
                
        return result



    def get_analytic_accounts(self, cr, uid, lines, company_id, context={}):
        """ from a bunch of lines, return all analytic accounts ids linked by those lines 
            Use it when you need analytic accounts in a financial approach. For a project approach, use get_project() above
            this is a facility to allow this module to be overridden to use projects instead of analytic accounts
        """
        return self.get_projects(cr, uid, lines, context)
        
        
        
    def get_projects(self, cr, uid, lines, context={}):
        """ from a bunch of lines, return all analytic accounts ids linked by those lines 
            this is an alias of get_analytic_accounts() called when AA are used in a project approach (contrary to a financial approach)
            this is a facility to allow this module to be overridden to use projects instead of analytic accounts
        """
        result = []
        
        for l in lines:
            if l.analytic_account_id and l.analytic_account_id.id not in result:
                result.append(l.analytic_account_id.id) 
                
        return result
    
    
    def get_versions(self, cr, uid, lines, context={}):
        """  from a bunch of lines, return all budgets' versions those lines belong to """
        version = []
        version_ids = []
        
        for l in lines:
            if l.budget_version_id and l.budget_version_id.id not in version_ids:
                version.append(l.budget_version_id) 
                version_ids.append(l.budget_version_id.id)
                
        return version
    
    
    
    
    def get_periods (self, cr, uid, ids, context={}):
        """return periods informations used by this budget lines.  (the periods are selected in the budget lines)"""
        
        periods = []
        periods_ids = []
        
        lines = self.browse(cr, uid, ids, context)
        for l in lines:
            if l.period_id.id not in periods_ids:
                periods.append(l.period_id)
                periods_ids.append(l.period_id.id)
        
        
        #sort periods by dates
        def byDateStart(first, second):
            if first.date_start > second.date_start:
                return 1
            elif first.date_start < second.date_start: 
                return -1
            return 0
        periods.sort(byDateStart)                

        
        return periods
    
    
    
    def _get_budget_currency_amount(self, cr, uid, ids, name, arg, context={}):
        """ return the line's amount xchanged in the budget's currency """ 
        res = {}
        
        #We get all values from DB
        objs =self.browse(cr, uid, ids)
        for obj in objs:
            budget_currency_id = obj.budget_version_id.currency_id.id

            
            #get the budget creation date in the right format
            t=datetime.now()
            budget_ref_date = t.timetuple()
            
            if obj.budget_version_id.ref_date:
                budget_ref_date = time.strptime(obj.budget_version_id.ref_date, "%Y-%m-%d")
                #xchange
            res[obj.id] = c2c_helper.exchange_currency(cr, obj.amount, obj.currency_id.id, budget_currency_id)
        return res
    
    
    
    def _get_budget_version_currency(self, cr, uid, context):
        """ return the default currency for this line of account. THe default currency is the currency set for the budget version if it exists """
        
        # if the budget currency is already set
        if 'currency_id' in context and context['currency_id'] != False:
            return context['currency_id']
            
        return False
 
        
    _name = "c2c_budget.line"
    _description = "Budget Lines"
    _columns = {
        'period_id'                 : fields.many2one('account.period', 'Period', required=True),
        'analytic_account_id'       : fields.many2one('account.analytic.account', 'Analytic Account'), 
        'budget_item_id'            : fields.many2one('c2c_budget.item', 'Budget Item', required=True),
        'name'                      : fields.char('Description', size=200),
        'amount'                    : fields.float('Amount', required=True),
        'currency_id'               : fields.many2one('res.currency', 'Currency', required=True),
        'amount_in_budget_currency' : fields.function(_get_budget_currency_amount, method=True, type='float', string='In Budget\'s Currency'),
        
        'budget_version_id'         : fields.many2one('c2c_budget.version', 'Budget Version', required=True),        
        }

    _defaults = {
        'currency_id'    : lambda self, cr, uid, context: self._get_budget_version_currency(cr, uid, context)
        }

    _order = 'name'
    
    
    def _check_item_in_budget_tree (self, cr, uid, ids):
        """ check if the line's budget item is in the budget's structure """
        
        lines = self.browse(cr, uid, ids)
        for l in lines:
                    
            #get list of budget items for this budget
            budget_item_object = self.pool.get('c2c_budget.item')
            flat_items_ids = budget_item_object.get_sub_items(cr, [l.budget_version_id.budget_id.budget_item_id.id])
            
            if l.budget_item_id.id not in flat_items_ids:
                return False
        return True
        
        
    
    def _check_period(self, cr, uid, ids):
        """ check if the line's period overlay the budget's period """
        
        lines = self.browse(cr, uid, ids)
        for l in lines:
            
            # if a line's period is entierly before the budget's period or entierly after it, the line's period does not overlay the budget's period
            if    (l.period_id.date_start < l.budget_version_id.budget_id.start_date and l.period_id.date_stop < l.budget_version_id.budget_id.start_date) \
               or (l.period_id.date_start > l.budget_version_id.budget_id.end_date and l.period_id.date_stop > l.budget_version_id.budget_id.end_date):
                return False
            
        return True


    def search(self, cr, user, args, offset=0, limit=None, order=None, context={}, count=False):
        """search through lines that belongs to accessible versions """
        
        lines_ids =  super(c2c_budget_line, self).search(cr, user, args, offset, limit, order, context, count)    

        #get versions the user can see, from versions, get periods then filter lines by those periods
        if len(lines_ids) > 0:
            version_obj = self.pool.get('c2c_budget.version')
            versions_ids = version_obj.search(cr, user, [], context=context)
            versions = version_obj.browse(cr, user, versions_ids, context=context)
            
            periods = []
            for v in versions:
                periods = periods + version_obj.get_periods (cr, user, v, context=context)
            lines = self.browse(cr, user, lines_ids, context=context)
            lines = self.filter_by_period(cr, user, lines, [p.id for p in periods], context)
            lines_ids = [l.id for l in lines]
        
        return lines_ids
                                                                      
    
    
    
    _constraints = [
            (_check_period, "The line's period must overlap the budget's start or end dates", ['period_id']),
            (_check_item_in_budget_tree, "The line's bugdet item must belong to the budget structure defined in the budget", ['budget_item_id'])
            
        ]
    
    
c2c_budget_line()