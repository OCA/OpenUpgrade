# -*- encoding: utf-8 -*-
##############################################################################
#
# Copyright (c) Camptocamp (http://www.camptocamp.com) All Rights Reserved.
#
# author: awu ported by nbessi
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



class wiz_account_detail(wizard.interface):
    """ a wizard that display a report that list projects and their invoices 
        this wizard is inspired (/copied) from 
        the class wiz_invoices_from_proj in 
        addons/specific_fct/wizard/open_specific_invoices.py
    """


    def _get_select_projects_ids(self, cr, uid, data, context):
        """ Return the list of projects selected before to call the wizard. """
        
        if not len(data['ids']):
            return {}
        pool = pooler.get_pool(cr.dbname)
        try :
            cr.execute(
                        "SELECT id from account_analytic_account \
                        where id in (%s)" , 
                        (",".join(map(str,data['ids'])),)
                        )
            projects_ids = cr.fetchall()
        except Exception, e:
            cr.rollback()
            raise wizard.except_wizard(
                                        'Error !', 
                                         str(e)
                                      )
        
        
        res = {'projects': [x[0] for x in projects_ids]}
        return res
            
        
    def _get_print_projects_ids(self, cr, uid, data, context):       
        """ return the list of projects selected in the wizard's 
            first form that match the criterias """
        
        #values from the form
        projects_ids = data['form']['projects'][0][2]
        open_only = data['form']['open_only']
        supplier_too = data['form']['supplier_too']
            
        values = {'ids': projects_ids, 
                  'open_only': open_only,
                  'supplier_too': supplier_too,
                 }
        return values

        
    _create_form = """<?xml version="1.0"?>
    <form string="Get projects details">
        <separator string="Filter By Project" colspan="4"/>
        <field name="projects" colspan="4" nolabel="1"/>
        <separator string="Filter Options" colspan="4"/>
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
                        'string':'Open Invoices Only', 
                        'type':'boolean'
                    },
        'supplier_too': {
                            'string':'Display Suppliers Invoices', 
                            'type':'boolean'
                        },
    }

    states = {
        'init' : {
            'actions' : [_get_select_projects_ids], 
            'result' : {
                            'type':'form', 'arch':_create_form, 
                            'fields':_create_fields, 
                            'state': [
                                        ('end','Cancel'),
                                        ('print','Open Report')
                                    ]
                        },
        },
        'print' : {
            'actions': [_get_print_projects_ids],
            'result': {
                            'type':'print', 
                            'report':'indicator.account.detail', 
                            'get_id_from_action':True, 
                            'state':'end'
                        },            
            },

    }
wiz_account_detail('indicator.account.detail')