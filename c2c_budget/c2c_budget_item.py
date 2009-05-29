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
import time
from c2c_reporting_tools.c2c_helper import *             
        
        

class c2c_budget_item(osv.osv):
    """ camptocamp budget item. This is a link between 
    budgets and financial accounts. """

    
    _name = "c2c_budget.item"  
    _description = "Budget items"
    _columns = {
        'code' : fields.char('Code', size=50, required=True),
        'name' : fields.char('Name', size=200,  required=True),
        'active' : fields.boolean('Active'),
        'parent_id' : fields.many2one('c2c_budget.item', 'Parent Item'),
        'children_ids' : fields.one2many(
                                            'c2c_budget.item', 
                                            'parent_id', 
                                            'Children Items'
                                        ),
        'account' : fields.many2many(
                                        'account.account', 
                                        'c2c_budget_item_account_rel', 
                                        'budget_item_id', 
                                        'account_id', 
                                        'Financial Account'
                                    ),
        'note' : fields.text('Notes'),
        'calculation' : fields.text('Calculation'),
        'type' : fields.selection(
                                    [
                                        ('view', 'View'),
                                        ('normal', 'Normal')
                                    ], 
                                    'Type',
                                     required=True
                                ),
        'sequence' : fields.integer('Sequence'),
        'style' : fields.selection(
                                        [
                                            ('normal', 'Normal'), 
                                            ('bold', 'Bold'), (
                                            'invisible', 'Invisible')
                                        ], 
                                        'Style', 
                                        required=True
                                    ),
            }

    _defaults = {
            'active'      : lambda *a: True, 
            'type'        : lambda *a: 'normal',
            'style'       : lambda *a: 'normal',
                 }

    _order = 'sequence,name'    
    
    def get_real_values_from_analytic_accounts(self, cr, uid, item_id, periods,\
        lines, company_id, currency_id, change_date, context={}):
        """return the sum of analytic move lines for 
        this item (and all subitems)"""
                
        # filter the budget lines to work on
        budget_line_obj = self.pool.get('c2c_budget.line')         
        budget_lines = budget_line_obj.filter_by_items(
                                                            cr, 
                                                            uid, 
                                                            lines, 
                                                            [item_id], 
                                                            context
                                                        )
        
        # get the list of Analytic accounts related to those lines
        aa_ids = budget_line_obj.get_analytic_accounts(
                                                            cr, 
                                                            uid, 
                                                            budget_lines, 
                                                            company_id, 
                                                            context
                                                        )
        
        #get accounts (and subaccounts) related to the given item (and subitems)
        general_accounts_ids = self.get_accounts(
                                                    cr, 
                                                    uid, 
                                                    [item_id], 
                                                    company_id, 
                                                    context
                                                )
        
        #get dates limits 
        start_date = None
        end_date = None
        for p in periods:
            if start_date is None or start_date > p.date_start:
                start_date = p.date_start
            if end_date is None or end_date < p.date_stop:
                end_date = p.date_stop
                
                
        #we have all informations to look for Analytic Accounts' lines
        aa_lines_obj = self.pool.get('account.analytic.line')
        aa_lines_ids = aa_lines_obj.search(
                        cr, 
                        uid, 
                        [
                            ('date', '>=', start_date),
                            ('date', '<=', end_date),
                            ('general_account_id', 'in', general_accounts_ids),
                            ('account_id', 'in', aa_ids)], 
                            context=context
                        )
        aa_lines = aa_lines_obj.browse(cr, uid, aa_lines_ids, context=context)
        
        #now we have the lines, let's add them
        result = 0
        for l in aa_lines:
            result += c2c_helper.exchange_currency(
                                                    cr, 
                                l.amount, 
                                l.general_account_id.company_id.currency_id.id,
                                 currency_id, 
                                 c2c_helper.parse_date(change_date)
                                )
        
        return result
        
        
    
    
    def get_real_values(self, cr, uid, item, periods, company_id, \
        currency_id, change_date, context={}):
        """return the sum of the account move lines for this item """
        
        result = 0
        
        # get the list of accounts and subaccounts linked to this item
        accounts = self.get_accounts(cr, uid,  [item.id], company_id, context)
        
        #get all move_lines linked to this item
        move_line_obj = self.pool.get('account.move.line')
        move_line_ids = move_line_obj.search(
                                cr, 
                                uid, 
                                [
                                    ('period_id', 'in', [p.id for p in periods]),
                                     ('account_id', 'in', accounts)
                                ]
                            )
        move_lines = move_line_obj.browse(cr, uid, move_line_ids, context=context)
        
        #sum all lines
        for l in move_lines:
            
            #multi company!
            if 'company_id' in move_line_obj._columns:
                line_currency_id = l.company_id.currency_id.id
            #get company's currency from account
            else: 
                line_currency_id = l.account_id.company_id.currency_id.id
                
            #debit ?
            if l.debit != 0:
                amount = l.debit
                sign = -1
                
            #credit ? 
            else: 
                amount = l.credit
                sign = 1

            result += sign * c2c_helper.exchange_currency(
                                            cr, 
                                            amount, 
                                            line_currency_id, 
                                            currency_id, 
                                            c2c_helper.parse_date(change_date)
                                        )
        
        return result
        
            
    
    def get_sub_items(self, cr, item_ids):
        """ return a flat list of ids of all items under 
        items in the tree structure """        
        parents_ids = item_ids
        
        items_ids = copy(parents_ids) 
        
        loop_counter = 0
        
        #for each "level" of parent
        while len(parents_ids) > 0:
            #get all the sub items of this level
            query = """SELECT id 
                       FROM c2c_budget_item 
                       WHERE parent_id IN ( %s ) 
                       AND active """ % ','.join(map(str,parents_ids))
            cr.execute(query)
            children_ids = map(lambda x: x[0], cr.fetchall())
            items_ids += children_ids
            
            #continue with next level            
            parents_ids = copy(children_ids)

            #count the loops to avoid infinit loops
            loop_counter += 1
            if (loop_counter > 100):
                raise osv.except_osv(
                'Recursion Error', 
                """It seems the item structure is recursive.
                Please check and correct it before to run this action again"""
                )
            
        return c2c_helper.unique(items_ids)
    
    
    
    def get_accounts(self, cr, uid,  item_ids, company_id, context={}):
        """return a list of accounts ids and their sub accounts 
        linked to items (item_ids) and their subitems """
        
        sub_items_ids = self.get_sub_items(cr, item_ids)
        
        sub_items = self.browse(cr, uid, sub_items_ids)
        #gather all account linked to all subitems
        ids = []
        for i in sub_items:
            ids+= map (lambda x:x.id, i.account)
        
        #get the list of sub accounts of gathered accounts
        account_flat_list = self.pool.get('account.account').\
            get_children_flat_list(
                                    cr, 
                                    uid, 
                                    ids, 
                                    company_id, 
                                    context
                                )
        
        #here is the list of all accounts and subaccounts linked to items and subitems
        return account_flat_list
    
    
    
    def compute_view_items(self, items, items_values):
        """ compute items (type "view") values that are based on calculations 
            return the items_values param where computed values 
            are added (or replaced) 
            items is a list of items objects
            items_values is a dictionnary item_id => item_value
        """
        
        #prepare the dictionnary of values for formula remplacement.
        # put in it normal items' values and view items' values that do not have formula
        value_dict = {}
        for i in items:
            if (i.type == 'normal' or (i.type== 'view' and ((not i.calculation)\
             or i.calculation.strip() == "")) ) \
             and i.code and i.code.strip() != '':
                value_dict[""+i.code] = items_values[i.id]
        #this loop allow to use view items' results in formulas. 
        #count the number of errors that append. Loop until 
        #the number remain constant (=error in formulas) 
        #or reach 0 (=nothing more to compute)        
        previousErrorCounter = 0
        while True:
            errorCounter = 0
        
            #look throught the items if there is formula to compute?
            for i in items: 
                #if this item is a view, we must maybe 
                #replace its value by a calculation (if not already done)
                if i.type == 'view' \
                and i.calculation \
                and i.calculation.strip() != "" \
                and i.code \
                and (i.code+"" not in value_dict):
                    
                    formula_ok = True
                    exec_env = {'result': 0}
                    #replace keys by values in formula
                    try:
                        formula = i.calculation % value_dict
                    except Exception, e:
                        formula_ok = False
                        errorCounter += 1
                    #try to run the formula
                    if formula_ok:
                        result = None
                        try: 
                            exec formula in exec_env
                        except Exception, e:
                            formula_ok = False
                            errorCounter += 1
                    #retrive formula result
                    if formula_ok:
                        items_values[i.id] = exec_env['result']
                        value_dict[""+i.code] = exec_env['result']
                    else: 
                        items_values[i.id] = 'error'
            
            #the number of errors in this loop equal to the previous loop. 
            #No chance to get better... let's exit the "while true" loop
            if errorCounter == previousErrorCounter:
                break
            else: 
                previousErrorCounter = errorCounter
                
        return items_values
    
    
    
    def get_sorted_list(self, cr, uid, root_id):
        """return a list of items sorted by sequence to be used in reports 
           Data are returned in a list 
           (value=dictionnary(keys='id','code',
           'name','level', sequence, type, style))
        """
        
        def bySequence(first, second):
            """callback function to sort """
            if first['sequence'] > second['sequence']:
                return 1
            elif first['sequence'] < second['sequence']:
                return -1
            return 0
                
                
        flat_tree = self.get_flat_tree(cr, uid, root_id)
        flat_tree.sort(bySequence)
        
        item_ids = map(lambda x:x['id'], flat_tree)
        
        return self.browse(cr, uid, item_ids)
        
        

    def  get_flat_tree(self, cr, uid, root_id, level=0):
        """ return informations about a buget items tree strcuture. 
Data are returned in a list 
(value=dictionnary(keys='id','code','name','level', sequence, type, style))
Data are sorted as in the pre-order walk
algorithm in order to allow to display easily the tree in rapports 
example: 
    root    
     |_node 1
        |_sub node 1
     |_node 2
     |_ ...

Do not specify the level param when you call this method, 
it is used for recursive calls
"""
            
        result = []

        
        #this method is recursive so for the first call, 
        #we must init result with the root node
        if (level == 0):
            query = """SELECT id, code, name, sequence, type, style, %s as level
                       FROM c2c_budget_item 
                       WHERE id = %s """ % (level, str(root_id))
                    
            cr.execute(query)            
            result.append(cr.dictfetchall()[0])
            level += 1


        #get children's data
        query = """SELECT id, code, name, sequence, type, style, %s as level
                   FROM c2c_budget_item 
                   WHERE parent_id = %s
                   AND active 
                   ORDER BY sequence """ % (level, str(root_id))
        cr.execute(query)
        query_result = cr.dictfetchall()
        
        for child in query_result:
            result.append(child)
            #recursive call to append the children right after the item
            result += self.get_flat_tree(cr, uid, child['id'], level+1)
            
        #check to avoid inifit loop
        if (level > 100):
            raise osv.except_osv(
                                    'Recursion Error', 
                                    'It seems the budget items structure \
                                    is recursive (or too deep). \
                                    Please check and correct it\
                                    before to run this action again'
                                )
                    
        return result 
        
    
    
    
    def _check_recursion(self, cr, uid, ids):
        """ use in _constraints[]: return false 
        if there is a recursion in the budget items structure """
        
        #use the parent check_recursion function defined in orm.py
        return super(c2c_budget_item,self).check_recursion(
                                                            cr,
                                                            uid,
                                                            ids,
                                                            parent='parent_id'
                                                        )
    
    
    
    _constraints = [
            (   _check_recursion, 
                'Error ! You can not create recursive\
                 budget items structure.', 
                ['parent_id']
            )
        ]
    
    
    
    def name_search(self, cr, user, name, args=None,\
        operator='ilike', context=None, limit=80):
        """search not only for a matching names but also 
        for a matching codes """
        
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
    
    
    
    def search(self, cr, user, args, offset=0, \
        limit=None, order=None, context=None, count=False):
        """ special search. If we search an item from the budget 
        version form (in the budget lines) 
        then the choice is reduce to periods
        that overlap the budget dates"""
        
        result = [] 
           
        parent_result = super(c2c_budget_item, self).search(cr, user, args, offset, limit, order, context, count)    
        #special search
        if context != None and 'budget_id' in context \
            and context['budget_id'] != False:
            
            budget = self.pool.get('c2c_budget').browse(
                                                        cr, 
                                                        user, 
                                                        context['budget_id'], 
                                                        context
                                                    )
                        
            allowed_items = self.get_sub_items(
                                                cr, 
                                                [budget.budget_item_id.id]
                                                )
            for i in parent_result:
                if i in allowed_items: 
                    result.append(i)                   
        #normal search
        else: 
            result = parent_result
        return result
    
    
    
    def unlink(self, cr, uid, ids, context={}):
        """ delete subitems and catch the ugly error in case
         of the item is in use in another object """
        
        #build a list of all sub items 
        sub_ids = []
        if type(ids) == int:
            ids = [ids]
        sub_ids = self.get_sub_items(cr, ids)
                        
        #delete item and all subitems
        try: 
            return super(c2c_budget_item, self).unlink(
                                                        cr, 
                                                        uid, 
                                                        sub_ids, 
                                                        context
                                                    )
        except: 
            raise osv.except_osv(
                                'Unable to delete the item', 
                                'At least one of the items you are trying to\
                                 delete or one of their subitems is still \
                                 referenced by another element. \
                                 Check there is no budget lines that link to \
                                 these items and there is no budget that use \
                                 these items as budget structure root.')
            

            


    
c2c_budget_item()
