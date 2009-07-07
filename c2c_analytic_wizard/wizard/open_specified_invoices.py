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
    
    #
    # open analytic lines from project
    #

class wiz_invoices_from_proj(wizard.interface):
    "list customer invoices related to project"

    def _get_proj(self,cr,uid,project_inst,accounts):
        """ get children account"""
        if project_inst.id not in accounts:
            accounts.append(project_inst.id)
        for account in project_inst.child_ids:
            accounts.append(account.id)
            accounts=self._get_proj(cr,uid,account,accounts)
        return accounts
    
    def _open_invoices(self, cr, uid, data, context):
        """ open related invoices"""
        
        pool = pooler.get_pool(cr.dbname)
        projects_ids = data['form']['projects'][0][2]
        open_only = data['form']['open_only']
        supplier_too = data['form']['supplier_too']
        if open_only:
            open_only_sql=" and inv.state = 'open' "
        else:
            open_only_sql=''
        if supplier_too:
            supplier_too_sql=" "
        else:
            supplier_too_sql=" inv.type='out_invoice' and "
        #we do not use orm for performance issues
        for project in pool.get('account.analytic.account').browse(
                                                                    cr, 
                                                                    uid, 
                                                                    projects_ids, 
                                                                    context
                                                                    ):
            accounts=[]
            accounts=self._get_proj(cr,uid,project,accounts)
            cr.execute("""
                            SELECT inv.id from account_invoice \
                            inv left join account_invoice_line \
                            l on (inv.id=l.invoice_id) 
                            where %s
                            (
                                l.account_analytic_id in (%s)
                            ) %s ;"""%(
                                        supplier_too_sql,','.join(map(str,accounts)),
                                        open_only_sql
                                      )
                        )
            
            lines = cr.fetchall()
            line_ids=[]
            for line in lines:
                line_ids.append(line[0])
            ids=line_ids
            if not ids:
                raise wizard.except_wizard('Warning', 'Nothing was found !')
            cr.execute(
                            "select id,name from ir_ui_view \
                            where model= 'account.invoice' \
                            and name = 'account.invoice.form.inherit'"
                        )
            view_res = cr.fetchone()

            value = {
                'domain': "[('type','=','out_invoice'),\
('id','in', ["+','.join(map(str,ids))+"])]",
                'name': 'Customer invoices',
                'view_type': 'form',
                'view_mode': 'tree,form',
                'res_model': 'account.invoice',
                'view_id': view_res,
                'type': 'ir.actions.act_window',
                'res_id':ids,
                'context': "{'type':'out_invoice'}"
            }
            return value
        
    def _get_project(self, cr, uid, data, context): 
        """ init defaults"""
        res = {'projects': data['ids']}
        return res

    _create_form = """<?xml version="1.0"?>
    <form string="Get customer invoices from project">
        <separator string="Choose projects you want to get invoices from" colspan="4"/>
        <field name="projects" colspan="4" nolabel="1"/>
        <separator string="Do you want only open invoice ?" colspan="4"/>
        <field name="open_only"/>
        <field name="supplier_too"/>
    </form>"""

    _create_fields = {
        'projects': {
                        'string':'Projects',
                         'type':'many2many', 
                         'required':'true', 
                         'relation':'account.analytic.account'
                    },
        'open_only': {
                        'string':'Open invoice only', 
                        'type':'boolean'
                    },
        'supplier_too': {
                            'string':'Supplier invoice too', 
                            'type':'boolean'
                        },
    }

    states = {
        'init' : {
            'actions' : [_get_project], 
            'result' : {
                        'type':'form', 
                        'arch':_create_form, 
                        'fields':_create_fields, 
                        'state': [
                                    ('end','Cancel'),
                                    ('showlines','Get invoices')
                                ]
                        },
        },
        'showlines' : {
            'actions' : [],
            'result' : {
                        'type':'action', 
                        'action':_open_invoices, 
                        'state':'end'
                     },
        },

    }
wiz_invoices_from_proj('open.specified.invoices')

# vim:noexpandtab:tw=0
