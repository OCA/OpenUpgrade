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
from copy import copy


class account_account(osv.osv):
    """add new methods to the base account_account object """

    _inherit = "account.account"

    
    def get_children_map(self, cr, uid, company_id, context={}, sql_filter=""):
        """ return a dictionnary mapping the parent relation between 
        accounts and their children """

        #build a dictionnary {parent_id -> [children_ids]}
        children_ids =  {}
        query = """SELECT rel.child_id, rel.parent_id
           FROM account_account_rel rel, 
           account_account aa, account_account aa2
           WHERE rel.parent_id = aa.id
           AND rel.child_id = aa2.id
           AND aa.company_id = %s
           AND aa2.company_id = %s
           AND aa.active 
           AND aa2.active
            %s """ % (company_id, company_id, sql_filter)
           
        cr.execute(query)
        for i in cr.fetchall():
            if i[1] not in children_ids:
                children_ids[i[1]] = []
            children_ids[i[1]].append(i[0])
        
        return children_ids
    
    
    def get_children_flat_list(self, cr, uid, ids, company_id, context={}):            
        """return a flat list of all accounts'ids above the 
        ones given in the account structure (included the one given in params)"""
        
        result= [] 
        
        children_map = self.get_children_map(cr, uid, company_id, context)
        
        #init the children array
        children = ids
        
        #while there is children, go deep in the structure
        while len(children) > 0:
            result += children
            
            #go deeper in the structure
            parents = copy(children)
            children = []
            for p in parents:
                if p in children_map:
                    children += children_map[p]
                
        #it may looks stupid tu do a search on ids to get ids... 
        #But it's not! It allows to apply access rules and rights on the accounts to not return protected results
        return self.search(cr, uid, [('id', 'in', result)], context=context)
    
    
    def name_search(self, cr, user, name='', args=None, operator='ilike', context=[], limit=80):    
        """raise the limit of the search if there is a limit define in the context"""
        
        current_limit = limit
        #if context : just in case context is None
        if context and 'limit' in context:
            current_limit = context['limit']
        return super(account_account, self).name_search(cr, user, name, args, operator, context, current_limit)    
    
    
account_account()        
        
        
    
class account_period(osv.osv):
    """ add new methods to the account_period base object """
    
    _name = 'account.period'
    _inherit = 'account.period'
    
    
    def search(self, cr, user, args, offset=0, limit=None, order=None, \
        context={}, count=False):
        """ special search. If we search a period from the budget version
         form (in the budget lines)  then the choice is reduce 
         to periods that overlap the budget dates"""
        
        result = [] 
           
        parent_result = super(account_period, self).search(cr, user, args, offset, limit, order, context, count)    

        #special search limited to a version
        if 'version_id' in context and context['version_id'] != False:
            
            #get version's periods
            version_obj = self.pool.get('c2c_budget.version')
            vesion = version_obj.browse(
                                            cr, 
                                            user, 
                                            context['version_id'], 
                                            context=context
                                        )
            allowed_periods = version_obj.get_periods(
                                                        cr, 
                                                        user, 
                                                        version, 
                                                        context
                                                    )
            allowed_periods_ids = [p.id for p in allowed_periods]
                                  
            #match version's period with parent search result  
            periods = self.browse(
                                    cr, 
                                    user, 
                                    parent_result, 
                                    context
                                )
            for p in periods:
                if p.id in allowed_periods_ids:
                    result.append(p.id)
                    
        #normal search
        else: 
            result = parent_result
                
        return result
    
    
account_period()
    