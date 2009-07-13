# -*- coding: utf-8 -*- 
##############################################################################
#
# Copyright (c) Camptocamp SA - Joel Grand-Guillaume porté par Nicolas Bessi 
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
from mx import DateTime
import netsvc
from osv import fields
from osv import osv


####################################################################################
#  employee activity
####################################################################################
class project_activity_al(osv.osv):
    """Class tha inhertis osv.osv and add activities to account analytic lines"""
    _name = "project.activity_al"
    _description = "Project activity"
    
    
    ## @param self The object pointer.
    ## @param cr a psycopg cursor.
    ## @param uid res.user.id that is currently loged
    ## @param account a browse record of an account
    ## @return a browse reccod list of the first parent that have an activites
    def _get_first_AA_wich_have_activity(self,cr,uid,account):
        """Return browse record list of activities
           of the account which have an activity set 
           (goes bottom up, child, then parent)
        """
        if account.activity_ids:
            return account
        else:
            if account.parent_id:
                return self._get_first_AA_wich_have_activity(cr,uid,account.parent_id)
            else:
                return False

        
    ## @param self The object pointer.
    ## @param cr a psycopg cursor.
    ## @param uid res.user.id that is currently loged
    ## @param name osv._obj name of the serached object
    ## @param args an arbitrary list that contains search criterium
    ## @param operator search operator 
    ## @param context an arbitrary context
    ## @param limit int of the search limit
    ## @return the result of name get
    def name_search(self, cr, uid, name, args=None, 
        operator='ilike', context=None, limit=80):
        """ Ovveride of osv.osv name serach function that do the search
            on the name of the activites """
        if not args:
            args=[]
        acc_ids=[]
        if not context:
            context={}
        if context.get('account_id',False):
            aa_obj = self.pool.get('account.analytic.account')
            account_id = aa_obj.browse(cr,uid,context.get('account_id',False))
            #take the account wich have activity_ids
            acc_who_matters=self._get_first_AA_wich_have_activity(
                                                                cr,
                                                                uid,
                                                                account_id
                                                            )
            if acc_who_matters:
                for i in acc_who_matters.activity_ids:
                    acc_ids.append(i.id)
        
        account = self.search(
                                cr, 
                                uid, 
                                    [
                                        ('code', '=', name),
                                        ('id','in',acc_ids)
                                    ]+args, 
                                limit=limit, 
                                context=context
                            )
        if not account:
            account = self.search(
                                    cr, 
                                    uid, 
                                    [
                                        ('name', 'ilike', '%%%s%%' % name),
                                        ('id','in',acc_ids)
                                    ]+args, 
                                    limit=limit, 
                                    context=context
                                )
        if not account:
            account = self.search(
                                    cr, 
                                    uid, 
                                    [
                                        ('id','in',acc_ids)
                                    ]+args, 
                                    limit=limit, 
                                    context=context
                                 )
        # For searching in parent also
        if not account:
            account = self.search(
                                    cr, 
                                    uid, 
                                    [
                                        ('name', 'ilike', '%%%s%%' % name)
                                    ]+args, 
                                    limit=limit, 
                                    context=context
                                 )
            newacc = account
            while newacc:
                newacc = self.search(
                                        cr, 
                                        uid, 
                                        [
                                            ('parent_id', 'in', newacc)
                                        ]+args, 
                                        limit=limit, 
                                        context=context
                                    )
                account+=newacc
            
        return self.name_get(cr, uid, account, context=context)
        
    _columns = {
        ## activity code
        'code': fields.char('Code', required=True, size=64),
        ## name of the code
        'name': fields.char('Activity', required=True, size=64,translate=True),
        ## parent activity
        'parent_id' : fields.many2one('project.activity_al', 'Parent activity'),
        ## link to account.analytic account
        'project_ids': fields.many2many(
                                            'account.analytic.account',
                                            'proj_activity_analytic_rel', 
                                            'activity_id', 'analytic_id', 
                                            'Concerned project'
                                         ),
        ## link to the children activites                                 
        'child_ids': fields.one2many(
                                        'project.activity_al', 
                                        'parent_id', 
                                        'Childs Activity'
                                    ),
    }
    
project_activity_al()

####################################################################################
#  Analytic account
####################################################################################

class account_analytic_account(osv.osv):
    """ Classe that override account.analytic.account 
    in order to add new attributes"""
    _name = 'account.analytic.account'
    _inherit = "account.analytic.account"
    
    _columns = {
        ## Link activity and project 
        'activity_ids': fields.many2many(
                                            'project.activity_al',
                                            'proj_activity_analytic_rel',
                                            'analytic_id',
                                            'activity_id',
                                            'Related activities'
                                        ),

    }

account_analytic_account()

####################################################################################
#  Account analytic line
####################################################################################
class account_analytic_line(osv.osv):
    """ Classe that override account.analytic.line 
    in order to add new attributes """
    _name = "account.analytic.line"
    _inherit = "account.analytic.line"

    _columns = {
        'activity' : fields.many2one('project.activity_al', 'Activity'),
    }
account_analytic_line()