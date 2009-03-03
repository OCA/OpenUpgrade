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
import netsvc
import time
import pooler
from osv import osv


class wiz_budgetlines_from_aa(wizard.interface):
    """ action in the Analytic accounts form that open a list of budget lines related to the AA"""

    def _get_children(self,cr,uid,project_inst,accounts):
        """ return the list of all analytic accounts below the one given by param in the analytic accounts structure"""
        if project_inst.id not in accounts:
            accounts.append(project_inst.id)
        for account in project_inst.child_ids:
            accounts.append(account.id)
            accounts=self._get_children(cr,uid,account,accounts)
        return accounts
    
        
    def _open_lines(self, cr, uid, data, context):
        """ get budget lines related to an analytic account (or to its children)"""
        pool = pooler.get_pool(cr.dbname)
    
    
        if not len(data['ids']):
            raise wizard.except_wizard('Missing analytic account', 'Select at least one analytic account to run this action')
        parent_accounts_ids=data['ids']
        
        # find AA's children recursively
        accounts_ids=[]
        for account in pool.get('account.analytic.account').browse(cr, uid, parent_accounts_ids, context):
            accounts_ids=self._get_children(cr,uid,account,accounts_ids)

        # Get selected budgets
        versions_ids = []
        if data['form']['versions'][0][2]:
            versions_ids = data['form']['versions'][0][2]
            
        #get limits
        period_start_id = None
        if data['form']['period_start']:
            period_start_id = data['form']['period_start']
            period_start = pool.get('account.period').browse(cr, uid, period_start_id, context)
        period_end_id = None
        if data['form']['period_end']:
            period_end_id  = data['form']['period_end']
            period_end = pool.get('account.period').browse(cr, uid, period_end_id, context)
        
        
        # Build query to get corresponding lines
        filter_accounts = "AND analytic_account_id in (%s)"%(','.join(map(str,accounts_ids)))
        
        filter_versions = ""
        if len(versions_ids) > 0:
            filter_versions = "AND budget_version_id in (%s)"%(','.join(map(str,versions_ids)))
            
        filter_from = ""
        if period_start_id != None:
            filter_from = "AND p.date_start >= '%s' " % period_start.date_start
        
        filter_to = ""
        if period_end_id != None:
            filter_to = "AND p.date_stop <= '%s' " % period_end.date_stop
        
        
        query = """SELECT bl.id, p.date_start, p.date_stop 
                   FROM c2c_budget_line bl, account_period p
                   WHERE bl.period_id = p.id
                   %s %s %s %s
        """ %(filter_accounts, filter_versions, filter_from, filter_to)
        cr.execute(query)
        lines = cr.dictfetchall()
        
        if len(lines) == 0:
            raise wizard.except_wizard('No result', 'Your selection return no result. Try again with different options')
             
        lines_ids = map(lambda a: a['id'], lines)
             
        # find periods in limits
        query = """ SELECT id, date_start, date_stop 
                    FROM account_period p 
                    WHERE TRUE
                    %s %s """ % (filter_from, filter_to)
        cr.execute(query)
        periods_ids = map(lambda a: a['id'], cr.dictfetchall())
             
             
             
             
        #build domain to limit results and new lines' choices
        domain=[]
        if len(accounts_ids) == 1: 
            domain.append("('analytic_account_id','=',%d)"%lines[0]['id'])
        elif len(accounts_ids) > 1:
            domain.append("('analytic_account_id','in',["+','.join(map(str,accounts_ids))+"])")
            
            
        if len(versions_ids) == 1:
            domain.append("('budget_version_id', '=', %d)" % versions_ids[0])
        elif len(versions_ids) > 1:
            domain.append("('budget_version_id', 'in',["+','.join(map(str,versions_ids))+"])")
          
        if len(periods_ids) == 1:
            domain.append("('period_id', '=', %d)" % periods_ids[0])
        elif len(periods_ids) > 1:
            domain.append("('period_id', 'in',["+','.join(map(str,periods_ids))+"])")
            
        domain_str = "[%s]"%','.join(map(str,domain))

        result = {
            'domain': domain_str,
            'name': 'Filtered Budgets Lines',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'c2c_budget.line',
            'view_id': False,
            'type': 'ir.actions.act_window',
            'res_id':lines_ids,
            'context':{'domain':domain_str},
        }
                
        return result

        
    _create_form = """<?xml version="1.0"?>
    <form title="Open selected planning lines" height="200" width="800">
        <separator string="Budgets Versions (empty for all)" colspan="4"/>
        <field name="versions" nolabel="1" colspan="4"/>
        <separator string="Limits" colspan="4"/>
        <field name="period_start"/>
        <field name="period_end"/>
    </form>"""

    _create_fields = {
        'versions':    {'string':'Budgets Versions', 'type':'many2many', 'relation':'c2c_budget.version'},
        'period_start':{'string':'Start Period',     'type':'many2one',  'relation':'account.period' },
        'period_end':  {'string':'End Period',       'type':'many2one',  'relation':'account.period'},
    }
        
    states = {
    
        'init' : {
            'actions':[],
            'result' : {'type':'form', 'arch':_create_form, 'fields':_create_fields, 'state': [('end','Cancel'),('showlines','Open budget lines')]},
        },
        'showlines' : {
            'actions' : [],
            'result' : {'type':'action', 'action':_open_lines, 'state':'end'},
        },

    }
    
wiz_budgetlines_from_aa('budgetlines.from.aa')