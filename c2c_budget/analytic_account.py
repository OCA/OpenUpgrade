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
from copy import copy


class analytic_account(osv.osv):
    """ add new methods to the base analytic_account object """

    _inherit = "account.analytic.account"
    
    def get_children_map(self, cr, uid, context={}):
        """ return a dictionnary mapping the parent relation between accounts and their children """

        #build a dictionnary {parent_id -> [children_ids]}
        children_ids =  {}
        anal_ids = self.search(cr, uid, [], context)
        anal_accounts = self.browse(cr, uid, anal_ids, context)
        
        for anal_account in anal_accounts: 
            if anal_account.parent_id:
                if anal_account.parent_id.id not in children_ids:
                    children_ids[anal_account.parent_id.id] = []
                children_ids[anal_account.parent_id.id].append(anal_account.id)
            
        
        return children_ids
    
    
    def get_children_flat_list(self, cr, uid, ids, context={}):            
        """return a flat list of all accounts'ids above the ones given in the account structure (included the one given in params)"""
        
        result= [] 
        
        children_map = self.get_children_map(cr, uid, context)
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
                
        return result
analytic_account()