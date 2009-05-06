# -*- coding: utf-8 -*- 
##############################################################################
#
# Copyright (c) Camptocamp SA - http://www.camptocamp.com
# Author: Arnaud Wüst ported by Nicolas Bessi
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
import time
import pooler


class c2c_budget(osv.osv):
    """ camptocamp budget. The module's main object.  """
    
    _name = "c2c_budget"
    _description = "Budget"
    _columns = {
        'code' : fields.char('Code', size=50),
        'name' : fields.char('Name', size=200, required=True),
        'active' : fields.boolean('Active'),
        'start_date' : fields.date('Start Date', required=True),
        'end_date' : fields.date('End Date', required=True),
        'budget_item_id' : fields.many2one(
                                            'c2c_budget.item', 
                                            'Budget Structure', 
                                            required=True
                                            ),
        'budget_version_ids' : fields.one2many(
                                                'c2c_budget.version', 
                                                'budget_id', 
                                                'Budget Versions', 
                                                 readonly=True
                                            ),
        'note'               : fields.text('Notes'),
        'create_date'        : fields.datetime('Creation Date', readonly=True)
        }
    
    _defaults = {
        'active' : lambda *a : True,         
        }
    
    _order = 'name'   
    

    def name_search(self, cr, user, name, args=None,\
        operator='ilike', context=None, limit=80):
        """search not only for a matching names but also for a matching codes """
                
        if not args:
            args=[]
        if not context:
            context={}
        ids = self.search(
                            cr, 
                            user, 
                            [('code',operator,name)]+ args, 
                            limit=limit, 
                            context=context
                        )
        ids += self.search(
                            cr, 
                            user, 
                            [('name',operator,name)]+ args, 
                            limit=limit, 
                            context=context
                        )
        return self.name_get(
                                cr, 
                                user, 
                                ids, 
                                context
                            )        

    
    
    def _check_start_end_dates(self, cr, uid, ids):
        """ check the start date is before the end date """
        lines = self.browse(cr, uid, ids)
        for l in lines:
            if l.end_date < l.start_date:
                return False
        return True        
     
    def get_periods(self, cr, uid, ids, context={}):
        """ return the list of budget's periods ordered by date_start"""
        
        period_obj = pooler.get_pool(cr.dbname).get('account.period')

        result = []

        if type(ids)==int:
            budget_ids = [ids]
            
        budgets = self.browse(cr, uid, budget_ids, context)
        
        start_date = None
        end_date = None
        
        for b in budgets:
            periods_ids = period_obj.search(
                                        cr, 
                                        uid, 
                                        [
                                            ('date_stop', '>', b.start_date), 
                                            ('date_start', '<', b.end_date)
                                        ], 
                                        order="date_start ASC"
                                    )
            result.append(period_obj.browse(cr, uid, periods_ids, context))
            
        if type(ids)==int:
            result = result[0]
        
        return result
    
    
    def get_periods_union(self, cr, uid, ids, context={}):
        """ return the list of budget's periods ordered by date_start 
            it returns a unique list that cover all given budgets ids
        """
        
        period_obj = pooler.get_pool(cr.dbname).get('account.period')

        result = []
        if type(ids)==int:
            budget_ids = [ids]
        else: 
            budget_ids = ids
            
        budgets = self.browse(cr, uid, budget_ids, context)

        #find the earliest start_date en latest end_date
        start_date = None
        end_date = None
        for b in budgets:
            if start_date is None or start_date > b.start_date:
                start_date = b.start_date
            if end_date is None or end_date < b.end_date:
                end_date = b.end_date
                   
                   
        if start_date is not None :            
            periods_ids = period_obj.search(
                                        cr, 
                                        uid, 
                                        [
                                            ('date_stop', '>', start_date), 
                                            ('date_start', '<', end_date)
                                        ], 
                                        order="date_start ASC"
                                    )
            result = period_obj.browse(cr, uid, periods_ids, context)
            
        if type(ids)==int:
            return result[0]
        else: 
            return result

                
        
        
    
    def unlink(self, cr, uid, ids, context={}):
        """delete all budget versions when deleting a budget """
        
        budget_version_obj = pooler.get_pool(cr.dbname).get('c2c_budget.version')
        lines_ids = budget_version_obj.search(
                                                cr, 
                                                uid, 
                                                [('budget_id', 'in', ids)], 
                                                context=context
                                            )
        
        budget_version_obj.unlink(cr, uid, lines_ids, context)
        return super(c2c_budget, self).unlink(cr, uid, ids, context)
        
             
     
        
    _constraints = [
        (_check_start_end_dates, 'Date Error: The end date is defined before the start date', ['start_date', 'end_date']),
    ]
    
c2c_budget()

