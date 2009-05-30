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

import wizard
from copy import copy
import pooler


_define_filters_form = '''<?xml version="1.0"?>
    <form string="Validate Budget Structure" width="400">
        <group colspan="4" col="4" string="Results">
            <separator string="Result To Display" colspan="4"/>
            <field name="result" colspan="4" nolabel="1" width="400" />
        </group>

        <group colspan="4" col="4" string="Filters">
            <separator string="Filter By Company" colspan="4"/>
            <field name="company" colspan="4" nolabel="1"/>
            <newline/>
            <separator string="Filter By Account Type" colspan="4"/>
            <field name="account_type" nolabel="1" colspan="4" height="200" widget="many2many" />
            <newline/>
        </group>
    </form>'''


_define_filters_fields = {
        'company': {'string':'Company', 'type':'many2one', 'relation':'res.company'}, 
        'account_type': {'string': 'Account Type', 'type':'one2many', 'relation': 'account.account.type', 'help': 'Filter results by account'},         
        'result': {'string':'Result To Display', 'type':'selection', 'selection':[('orphans','Orphans Accounts'),('twice','Accounts Linked Twice')], 'default': lambda *args: 'orphans', 'mandatory': True}
        }


class wiz_validate_budget_structure(wizard.interface):
    """ this wizard allow to validate a budget structure by displaying either accounts linked twice in the structure or accounts not linked in the structure """
    
    linked_accounts = []
    account_children_map = []
    account_parents_map = []
    root_accounts = []
    cr = None
    
    
    def _check_item_selection(self, cr, uid, data, context):
        """ test if there is one and only one item selected when this wizard is run """
        if len(data['ids']) != 1: 
             raise wizard.except_wizard('Selection Error', 'You need to select one, and only one, budget structure to run this action')
        return {}
    
        
       
    def _show_result(self, cr, uid, data, context):
        """ return the result of the wizard. Either the list of orphan accounts or the duplicate accounts """
        self.cr = cr
        
        sql_filters =     self._get_sql_filters(data['form']['company'], data['form']['account_type'][0][2])
        sql_filters_aa2 = self._get_sql_filters(data['form']['company'], data['form']['account_type'][0][2], 'aa2')
        
        root_id = data['ids'][0]
        
        pool = pooler.get_pool(cr.dbname)
        budget_item_object = pool.get('c2c_budget.item')
        
        flat_items_ids = budget_item_object.get_sub_items(cr, [root_id])
        
        #init all the account linked to the item structure
        self.linked_accounts = self._get_linked_accounts(cr, uid, flat_items_ids, sql_filters, context=context)
        
        self.account_children_map = self._get_children_map(cr, uid, sql_filters+sql_filters_aa2, context=context)
        
        self.root_accounts = self._get_root_accounts(cr, uid, sql_filters, context=context)

        
        #find the orphans account
        if data['form']['result'] == 'orphans' :
            result_ids = self._get_orphan_accounts(sql_filters)
            result_text = 'Orphan accounts'
            
        #find the duplicate account
        else: 
            result_ids = self._get_duplicate_accounts(sql_filters)
            result_text = 'Duplicate accounts'
        
        return {
            'domain': "[('id','in', ["+','.join(map(str,result_ids))+"])]",
            'name': result_text,
            'view_type': 'form',
            'view_mode': 'tree',
            'res_model': 'account.account',
            'view_id': False,
            'context': "{'type':'out_invoice'}",
            'type': 'ir.actions.act_window',
            'res_id': result_ids
        }
        
        
        
    
    def _get_duplicate_accounts(self, sql_filter):
        """ return a list of accounts linked twice by the budget structure. Taking in account that a linked account link also all its children recursively"""
        
        duplicate = []
        
        for i in self.root_accounts:
            duplicate += self._get_duplicate_in_tree(i, sql_filter, 0, 0)
            
        return duplicate
        
        
    def _get_duplicate_in_tree(self, root_account_id, sql_filter, deep_counter, reference_counter):
        """ return account that are references more than once in the account structure. Taking in account that an item linked to an account also link all the account's sub structure"""
        
        duplicate =[]
        
        #check if we are too deep in the structure, we raise an error because it seems to be a cyclic structure
        if (deep_counter > 100):
            raise wizard.except_wizard('Recursion Error', 'It seems the account structure is recursive. Please check and correct it before to run this action again')
        
        if root_account_id in self.linked_accounts:
            reference_counter += self.linked_accounts.count(root_account_id)
            
        #if this account as more than 1 reference, it is duplicate. No need to go deeper, all sub structures are duplicated too
        if reference_counter > 1:
            return [root_account_id]
        
        #let's go deeper to find duplicated accounts
        if root_account_id in self.account_children_map:
            root_children = self.account_children_map[root_account_id]        
            for child in root_children:
                duplicate += self._get_duplicate_in_tree(child, sql_filter, deep_counter+1, reference_counter)
            
        return duplicate
        
        


    def _get_orphan_in_tree(self, root_account_id, sql_filter, deep_counter):
        """ return the accounts that are below the root_account_id in the tree structure and not linked to a item """ 
        
        orphans = []
        root_children = []
        
        #check if we are too deep in the structure, we raise an error because it smeels cyclic structure
        if (deep_counter > 100):
            raise wizard.except_wizard('Recursion Error', 'It seems the account structure is recursive. Please check and correct it before to run this action again')
        
        #if this account is linked, there is no orphans deeper
        if root_account_id in self.linked_accounts: 
            return []
            
        #if there is children, we go to find orphans deeper
        if root_account_id in self.account_children_map:
            root_children = self.account_children_map[root_account_id]
            #search orphans in all our children
            for child in root_children:
                orphans += self._get_orphan_in_tree(child, sql_filter, deep_counter+1)
 
 
        #check if all children are orphans. if some of them are not orphans, then return the list of orphans children
        # otherwise, return the root id
        for i in root_children:
            if i not in orphans:
                return orphans
            
        #if all our children are orphans, then do not return their ids but only our
        return [root_account_id] 
                    
    
    
    
        
    def _get_orphan_accounts(self, sql_filters):
        """ return a list of orphan account """

        orphans = []
        
        for i in self.root_accounts:
            orphans += self._get_orphan_in_tree(i, sql_filters, 0)
            
        return orphans

        
        
        
    def _get_root_accounts(self, cr, uid, sql_filters, context={}):
        """ return all account that do not have parents """
        
        query = """ SELECT distinct(aa.id)
                    FROM account_account aa LEFT OUTER JOIN account_account_rel rel ON (aa.id = rel.child_id)
                    WHERE rel.child_id IS NULL
                    AND aa.active
                    %s """ % sql_filters
        self.cr.execute(query)
        
        result = map(lambda x: x[0], self.cr.fetchall())

        #looks weird to search on ids to get ids, uh? 
        #it because it applies access rules and manage rights
        pool = pooler.get_pool(cr.dbname)
        account_obj = pool.get('account.account')   
        return account_obj.search(cr, uid, [('id', 'in', result)], context=context)
                    

    
    def _get_children_map(self, cr, uid, sql_filter, context={}):
        """ return a dictionnary mapping the parent relation between accounts and their children """

        #build a dictionnary {parent_id -> [children_ids]}
        children_ids =  {}
        query = """SELECT rel.child_id, rel.parent_id
           FROM account_account_rel rel, account_account aa, account_account aa2
           WHERE rel.parent_id = aa.id
           AND rel.child_id = aa2.id
           AND aa.active 
           AND aa2.active %s """ % (sql_filter)
           
        self.cr.execute(query)
        for i in self.cr.fetchall():
            if i[1] not in children_ids:
                children_ids[i[1]] = []
            children_ids[i[1]].append(i[0])
        

        return children_ids
    
    
    
    
    def _get_sql_filters(self, company_id_filter = False, account_ids_filter = [], table = 'aa'):
        """ return a piece of sql to use in queries to filter results """
        
        #should we filter accounts on a company?
        company_sql = ""
        if company_id_filter != False:
            company_sql = " AND %s.company_id = %s " % (table, company_id_filter)
            
            
        #should we filter accounts on type? 
        account_type_sql = ""
        if len(account_ids_filter) > 0:
            #get the type codes
            query = """ SELECT code, id 
                        FROM account_account_type 
                        WHERE id IN (%s) """ % (','.join(map(str, account_ids_filter)))
            self.cr.execute(query)
            
            account_type_sql = " AND %s.type IN (%s) " % (table, ','.join(map(lambda x: "'"+str(x)+"'", map(lambda x: x[0], self.cr.fetchall()))))
        
        return company_sql+account_type_sql
    
        
    
    def _get_linked_accounts(self, cr, uid, item_ids, sql_filters, context={}):
        """return a flat list of all accounts linked to a list of items """
                
        # we get all accounts directly linked to items
        query = """SELECT aa.id
                   FROM c2c_budget_item_account_rel bh, account_account aa
                   WHERE bh.account_id = aa.id
                       AND bh.budget_item_id IN (%s) 
                       AND aa.active
                       %s """ % (','.join(map(str,item_ids)), sql_filters)
        self.cr.execute(query)
        linked_accounts_ids = map(lambda x: x[0], self.cr.fetchall())
        

        #looks weird to search on ids to get ids, uh? 
        #it because doing so applies access rules and manage rights
        pool = pooler.get_pool(cr.dbname)
        account_obj = pool.get('account.account')   
        return account_obj.search(cr, uid, [('id', 'in', linked_accounts_ids)], context=context)
        
    
            
    states = {
        # the user choose the filters
        'init': {
            'actions': [_check_item_selection],
             'result': {'type': 'form', 'arch':_define_filters_form, 'fields':_define_filters_fields, 'state':[('end','Cancel', 'gtk-cancel'), ('show_result','Ok', 'gtk-go-forward', True)]}
        },
        # open windows to show orphans account and account used twice
        'show_result' : {
            'actions' : [],
            'result' : {'type':'action', 'action':_show_result, 'state':'end'},
        },
        
    }
    
    
wiz_validate_budget_structure('c2c_budget.validate_budget_structure');    
