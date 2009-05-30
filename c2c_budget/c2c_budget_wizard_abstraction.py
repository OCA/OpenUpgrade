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
import time
import pooler


class c2c_budget_wizard_abstraction(osv.osv):
    """ This object define parts of wizards forms 
    and process that can be override. 
    It is used to replace analytic_account by 
    projects for some of ours customers """
    
    _name = "c2c_budget.wizard_abstraction"
    _description = "Wizard Abstraction"
    _columns = {}
    _defaults = {}
    
    
    def budget_vs_real_get_form(self, cr, uid, data, context={}):
        """ return a piece of form used in the budget_vs_real wizard """

        return """<separator string="Select Analytic Accounts 
        (leave empty to get all accounts in use)" 
        colspan="4"/>    
        <field name="split_by_aa" />
        <newline/> 
        <field name="analytic_accounts" 
            colspan="4" nolabel="1" width="600" height="200"/>
        <newline/> 
        """
               
               
    def budget_vs_real_get_fields(self, cr, uid, data, context={}):
        """ return some fields of form used in the budget_vs_real wizard """
 
        fields = {}
        fields['analytic_accounts'] = {
                                        'string':'Analytic Accounts', 
                                        'type':'many2many', 
                                        'relation':'account.analytic.account'
                                      }        
        fields['split_by_aa'] = {
                                    'string':'Split by Analytic Accounts', 
                                    'type':'boolean'
                                }        
        return fields


    def budget_by_period_get_form(self, cr, uid, data, context={}):
        """ return a piece of form used in the budget_by_period wizard """

        return """<separator string="Select Analytic Accounts 
        (leave empty to get all accounts in use)" colspan="4"/>    
        <field name="split_by_aa" />
        <newline/> 
        <field name="analytic_accounts" 
            colspan="4" nolabel="1" width="600" height="200"/>
        <newline/> 
        """
               
               
    def budget_by_period_get_fields(self, cr, uid, data, context={}):
        """ return some fields of form used in the budget_by_period wizard """
 
        fields = {}
        fields['analytic_accounts'] = {
                                        'string':'Analytic Accounts', 
                                        'type':'many2many', 
                                        'relation':'account.analytic.account'
                                    }        
        fields['split_by_aa'] = {
                                    'string':'Split by Analytic Accounts', 
                                    'type':'boolean'
                                }        
        return fields
    
    
    def advanced_search_get_form(self, cr, uid, data, context={}):
        """ return a piece of form used in the advanced_search """
        
        return """<separator string="Choose Analytic Accounts 
              (leave empty to not filter)" colspan="2"/>
              <separator string="Choose versions (leave empty to not filter)" colspan="2"/>
              <field name="analytic_accounts" nolabel="1" colspan="2" width="400"/>
              <field name="versions" nolabel="1" colspan="2" width="400" height="150"/>
              <field name="empty_aa_too" colspan="2"/>"""
        
        
    def advanced_search_get_fields(self, cr, uid, data, context={}):
        """ return some fields of form used in the advanced_search wizard """
        
        fields = {}
        fields['analytic_accounts'] = {
                                        'string':'Analytic Accounts', 
                                        'type':'many2many', 
                                        'relation':'account.analytic.account'
                                    }
        fields['empty_aa_too'] = {
                                    'string':'Include Lines Without Analytic Account', 
                                    'type':'boolean'
                                }
        fields['versions'] = {
                                'string':'Versions', 
                                'type':'many2many', 
                                'relation':'c2c_budget.version'
                            }
        return fields

    
c2c_budget_wizard_abstraction()