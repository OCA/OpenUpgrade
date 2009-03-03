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
import pooler
import time


class c2c_budget_version(osv.osv):
    """ camptocamp budget version. A budget version is a budget made at a given time for a given company. 
        It also can have its own currency """
    
    
    _name = "c2c_budget.version"
    _description = "Budget versions"
    _columns = {
        'code'               : fields.char('Code', size=50),
        'name'               : fields.char('Version Name', size=200,  required=True ),
        'budget_id'          : fields.many2one('c2c_budget', 'Budget',  required=True),
        'currency_id'        : fields.many2one('res.currency', 'Currency', required=True),
        'company_id'         : fields.many2one('res.company', 'Company',  required=True),
        'user_id'            : fields.many2one('res.users', 'User In Charge'),
        'budget_line_ids'    : fields.one2many('c2c_budget.line', 'budget_version_id', 'Budget Lines'),
        'note'               : fields.text('Notes'),
        'create_date'        : fields.datetime('Creation Date', readonly=True),
        'ref_date'           : fields.date('Reference Date', required=True),
        }

    _order = 'name'
    
    _defaults = { 
        'ref_date' : lambda *a: time.strftime("%Y-%m-%d"),
                }


    
    def get_period(self, cr, uid, version, date, context={}):
        """ return the period corresponding to the given date for the given version """
        
        period_obj = self.pool.get('account.period')    
        period_ids = period_obj.search( cr, uid,  [('date_start', '<=', date), ('date_stop', '>=', date)], context=context)
        periods_tmp = period_obj.browse(cr, uid, period_ids, context=context)
        if len(periods_tmp) > 0:
            return periods_tmp[0]
        return None
      
    
    
    def get_periods (self, cr, uid, version, context={}):
        """return periods informations used by this version. (the periods are those between start and end dates defined in budget)"""
        
        budget_obj = self.pool.get('c2c_budget')        
        return budget_obj.get_periods(cr, uid, version.budget_id.id)
 
 
        
    def get_next_periods (self, cr, uid,  version, start_period, periods_nbr, context={}):
        """ return a list of "periods_nbr" periods that follow the "start_period" for the given version """
        
        period_obj = self.pool.get('account.period')        
        period_ids = period_obj.search(cr, uid, [('date_start', '>', start_period.date_start)], order="date_start ASC", limit=periods_nbr, context=context)
        return period_obj.browse(cr, uid, period_ids, context)
         
 
        
    def get_previous_period(self, cr, uid, version, period, context={}):
        """ return the period that preceed the one given in param. 
            return None if there is no preceeding period defined """

        period_obj = self.pool.get('account.period')        
        
        ids = period_obj.search(cr, uid, [('date_stop','<',period.date_start)], order="date_start DESC")
        periods = period_obj.browse(cr, uid, ids, context)
        if len(periods) > 0:
            return periods[0]
        return None
    
    
    
    def get_next_period(self, cr, uid, version, period, context={}):
        """ return the period that follow the one given in param. 
            return None if there is no next period defined """
        nexts = self.get_next_periods(cr, uid, version, period, 1, context)
        if len(nexts) > 0:
            return nexts[0]
        return None        
        
        

    def get_filtered_budget_values(self, cr,uid, version, lines, period_start=None, period_end=None, context={}):
        """ for a given version compute items' values on lines between period_start and period_end included 
            version is a budget_version object
            lines is a list of budget_lines objects to work on
            period_start is a c2c_budget.period object
            period_end is a c2c_budget.period object
            return a dict: item_id => value
        """
        
        #find periods used by this version that stand between period_start and period_end included.
        filtered_periods= []
        periods = self.get_periods(cr, uid, version, context)
        for p in periods:
            if (period_start is None or p.date_start >= period_start.date_start ) and (period_end is None or p.date_stop <= period_end.date_stop):
                filtered_periods.append(p)
        
        #get lines related to this periods
        budget_lines_obj = pooler.get_pool(cr.dbname).get('c2c_budget.line')        
        filtered_lines = budget_lines_obj.filter_by_period(cr, uid, lines, [x.id for x in filtered_periods])
        
        #compute budget values on those lines
        return self.get_budget_values(cr, uid, version, filtered_lines, context)
             

    
    def get_budget_values(self, cr, uid, version, lines, context={}):
        """ for a given version compute items' values on lines 
            version is a budget_version object
            lines is a list of budget_lines objects to work on
            return a dict: item_id => value
        """

        
        budget_item_obj = self.pool.get('c2c_budget.item')        
        items = budget_item_obj.get_sorted_list(cr, uid, version.budget_id.budget_item_id.id)            

        #init results with 0
        items_results = dict(map(lambda x:(x.id, 0), items))

        
        # for each items
        for item in items:
            sub_items_ids = budget_item_obj.get_sub_items(cr, [item.id])
    
            #go through all lines
            for l in lines:
                # if the line belongs to this version and the line belongs to this item or subitem
                if l.budget_version_id.id == version.id and l.budget_item_id.id in sub_items_ids:
                    items_results[item.id] += l.amount_in_budget_currency
    
        #complete results with calculated items
        result = budget_item_obj.compute_view_items(items, items_results)
        return result
        
        
        
        
    def get_real_values_from_analytic_accounts(self, cr, uid, version, lines, context={}):
        """ return the values from the analytic accounts """
        
        budget_item_obj = self.pool.get('c2c_budget.item')        
        items = budget_item_obj.get_sorted_list(cr, uid, version.budget_id.budget_item_id.id)            
                
        #init results with 0
        items_results = dict(map(lambda x:(x.id, 0), items))
        
        budget_lines_obj = pooler.get_pool(cr.dbname).get('c2c_budget.line')
        periods = self.get_periods(cr, uid, version, context)
        
        #foreach item in the structure
        for item in items:
            items_results[item.id] = budget_item_obj.get_real_values_from_analytic_accounts(cr, uid, item.id, periods, lines, version.company_id.id, version.currency_id.id, version.ref_date, context=context)
        
        #complete results with calculated items
        result = budget_item_obj.compute_view_items(items, items_results)
        return result



    def get_real_values(self, cr, uid, version, lines, context={}):
        """ return the values from the general account """
        
        budget_item_obj = self.pool.get('c2c_budget.item')        
        items = budget_item_obj.get_sorted_list(cr, uid, version.budget_id.budget_item_id.id)            
    
        #init results with 0
        items_results = dict(map(lambda x:(x.id, 0), items))
        
        budget_lines_obj = pooler.get_pool(cr.dbname).get('c2c_budget.line')
        periods = self.get_periods(cr, uid, version, context)
        
        #foreach item in the structure
        for item in items:
            items_results[item.id] = budget_item_obj.get_real_values(cr, uid, item, periods, version.company_id.id, version.currency_id.id, version.ref_date, context=context)
        
        #complete results with calculated items
        result = budget_item_obj.compute_view_items(items, items_results)
        return result
                
            
    
    def get_percent_values(self, cr, uid, ref_datas, ref_id):
        """ build a dictionnary item_id => value that compare each values of ref_datas to one of them.
            ref_datas is a dictionnary as get_budget_values() returns
            ref_id is one of the keys of ref_datas. 
        """
        result = {}
        
        ref_value = 1
        if ref_id in ref_datas:
            ref_value = ref_datas[ref_id]
        
        # % calculation is impossible on a 0 value or on texts (for exemple: "error!")
        for id in ref_datas:
            try :
                result[id] = (ref_datas[id] / ref_value) * 100
            except: 
                result[id] = 'error'
                        
        return result
    
    
    def name_search(self, cr, user, name, args=None, operator='ilike', context=None, limit=80):
        """search not only for a matching names but also for a matching codes. Search also in budget names """
                
        if not args:
            args=[]
        if not context:
            context={}
            
        ids = self.search(cr, user, [('name',operator,name)]+ args, limit=limit, context=context)
        
        if len(ids) < limit:
            ids += self.search(cr, user, [('code',operator,name)]+ args, limit=limit, context=context)
            
                
        ids = ids[:limit]
        return self.name_get(cr, user, ids, context)        

    
    
    def unlink(self, cr, uid, ids, context={}):
        """delete all budget lines when deleting a budget version """
        
        budget_lines_obj = pooler.get_pool(cr.dbname).get('c2c_budget.line')
        lines_ids = budget_lines_obj.search(cr, uid, [('budget_version_id', 'in', ids)], context=context)
        budget_lines_obj.unlink(cr, uid, lines_ids, context)
        return super(c2c_budget_version, self).unlink(cr, uid, ids, context)
                
        
        
    
c2c_budget_version()