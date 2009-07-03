# -*- encoding: utf-8 -*-
##############################################################################
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

class wiz_analytic_line_from_proj(wizard.interface):
    """ Get AA line to be reinvoiced or invoiced from AA"""
    
    def _get_proj(self,cr,uid,project_inst,accounts):
        """recursive function that will retriev all childrens
         accounts"""
        if project_inst.id not in accounts:
            accounts.append(project_inst.id)
        for account in project_inst.child_ids:
            accounts.append(account.id)
            accounts=self._get_proj(cr,uid,account,accounts)
        return accounts
        
    def _open_lines(self, cr, uid, data, context):
        """ Return all the line to be invoice from the aa """
        pool = pooler.get_pool(cr.dbname)
        
        if not len(data['ids']):
            raise wizard.except_wizard(
                            'Missing analytic account', 
                            'Select at least one project to obtain analytic line'
                            )

        projects_ids = data['ids']
        if len(projects_ids) >1:
            raise wizard.except_wizard(
                        'Too much analytic account', 
                        'Select only one project to obtain analytic lines\
                         (takes the parent project)'
                                    )
        res = {'projects': [x[0] for x in projects_ids]}
        projects_ids = [x[0] for x in projects_ids]
        users_ids = data['form']['users'][0][2]
        ## Generating where clause data
        if users_ids:
            users_sql=' and line.user_id in ('+','.join(map(str,users_ids))+') '
        else:
            users_sql=''
        products_ids = data['form']['products'][0][2]
        if products_ids:
            products_sql=' and line.product_id in ('+','.join(map(str,products_ids))+') '
        else:
            products_sql=''
        for project in pool.get('account.analytic.account').browse(cr, uid, projects_ids, context):
            accounts=[]
            accounts=self._get_proj(cr,uid,project,accounts)
            # depends on selected options
            if data['form']['include_invoiced']:
                clause_include_invoiced = ' '
            else:
                clause_include_invoiced = ' and line.invoice_id is null '

            if data['form']['include_null_factor']:
                clause_include_null_factor = ' '
            else:
                clause_include_null_factor = ' and line.to_invoice is not null '
            try : 
                if not data['form']['include_purchase']:
                    cr.execute(
                                """SELECT line.id 
                                from account_analytic_line as line 
                                join account_analytic_journal 
                                on line.journal_id = account_analytic_journal.id
                                where line.account_id in (%s) %s %s %s %s 
                                and (account_analytic_journal.type='general')
                    """%(
                            ','.join(map(str,accounts)),
                            clause_include_invoiced,
                            users_sql,
                            clause_include_null_factor,
                            products_sql
                        )
                    )
                else:
                    cr.execute(
                                """SELECT line.id from account_analytic_line as line 
                                join account_analytic_journal 
                                on line.journal_id = account_analytic_journal.id 
                                where line.account_id in (%s) %s %s %s %s 
                                and (account_analytic_journal.type='general' 
                                or account_analytic_journal.type='purchase')
                    """%(
                            ','.join(map(str,accounts)),
                            clause_include_invoiced,
                            users_sql,
                            clause_include_null_factor,
                            products_sql
                        )
                    )
                lines = cr.fetchall()
            except Exception, e :
                cr.rollback()
                raise wizard.except_wizard(
                                            'Error !', 
                                             str(e)
                                            )
            line_ids=[]
            for line in lines:
                line_ids.append(line[0])
            ids=line_ids
            if not ids:
                raise wizard.except_wizard('Warning', 'Nothing was found !')
            value = {
                'domain': "[('id','in', ["+','.join(map(str,ids))+"])]",
                'name': 'Open uninvoiced lines',
                'view_type': 'form',
                'view_mode': 'tree,form',
                'res_model': 'account.analytic.line',
                'view_id': False,
                'type': 'ir.actions.act_window',
                'res_id':ids
            }
            return value
        

    _create_form = """<?xml version="1.0"?>
    <form string="Get uninvoiced analytic lines (on general et purshase AA journal)" height="200" width="600">
        <separator string="Choose users you want to make 
a filter on (empty for all)" colspan="4"/>
        <field name="users" colspan="4" nolabel="1"/>
        <separator string="Choose function you want to make 
a filter on (empty for all)" colspan="4"/>
        <field name="products" colspan="4" nolabel="1" 
        domain="[('categ_id','like','Service')]" />
        <separator string="Choose specific options for line selecting ?" 
        colspan="4"/>
        <field name="include_invoiced"/>
        <field name="include_null_factor"/>
        <field name="include_purchase"/>
    </form>"""

    _create_fields = {
        'users': {
                    'string':'Users', 
                    'type':'many2many', 
                    'relation':'res.users'
                  },
        'products': {
                        'string':'Function', 
                        'type':'many2many', 
                        'relation':'product.product'
                    },
        'include_purchase':  {
                            'string':'Include all purchase and expense to invoice',
                            'type':'boolean'
                            },
        'include_invoiced': {
                            'string':'Include invoiced lines', 
                            'type':'boolean'
                            },
        'include_null_factor': {
                                'string':'Include lines with null invoicing factor', 
                                'type':'boolean'
                                },
    }

    states = {
        'init' : {
            'result' : {
                            'type':'form', 
                            'arch':_create_form, 
                            'fields':_create_fields, 
                            'state': [
                                        ('end','Cancel'),
                                        ('showlines','Get uninvoiced lines')
                                    ]
                        },
        },
        'showlines' : {
            'actions' : [],
            'result' : {
                        'type':'action', 
                        'action':_open_lines, 
                        'state':'end'
                        },
        },

    }
wiz_analytic_line_from_proj('open.specified.analytic.line')