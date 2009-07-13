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
import pooler
import time
import osv
    

#
# assign analytic line to invoice from analytic line
#

class wiz_associate_analytic_line_from(wizard.interface):
    """assign analytic line to invoice from analytic line"""

    def _associate(self, cr, uid, data, context):
        """ function that will fill the field invoice_id of analytic lines"""
        if len (data['ids'])<1:
            raise wizard.except_wizard(
                                        'Error !', 
                                        'You must select at leat one line !'
                                    )
        try :
            pool = pooler.get_pool(cr.dbname)
            line_ids = data['ids']
            line_obj=pool.get('account.analytic.line')
            vals =  {'invoice_id': data['form']['invoice']}
            for line_id in line_ids:
                line_obj.write(
                                cr, 
                                uid, 
                                line_id,
                                vals
                            )
            return  {
                    'domain': "[('id','=', "+str(data['form']['invoice'])+")]",
                    'name': 'Invoices',
                    'view_type': 'form',
                    'view_mode': 'tree,form',
                    'res_model': 'account.invoice',
                    'view_id': False,
                    'type': 'ir.actions.act_window'
                }
        except Exception, e:
            raise wizard.except_wizard(
                                        'Error !', 
                                         str(e.name)+' '+str(e.value)
                                      )

    _create_form = """<?xml version="1.0"?>
    <form string="Associate lines to the selected invoice">
        <separator string="Choose invoice you want to assign to" colspan="4"/>
        <field name="invoice" colspan="4"/>
    </form>"""

    _create_fields = {
        'invoice': {
                        'string':'Invoice', 
                        'type':'many2one', 
                        'required':'true', 
                        'relation':'account.invoice'
                    },
    }

    states = {
        'init' : {
            'actions' : [], 
            'result' : {
                        'type':'form', 
                        'arch':_create_form, 
                        'fields':_create_fields, 
                        'state': [
                                    ('end','Cancel'),
                                    ('create','Assign those lines')
                                ]
                        },
        },
        'create' : {
            'actions' : [],
            'result' : {
                            'type':'action', 
                            'action':_associate, 
                            'state':'end'
                        },
        },
    }
wiz_associate_analytic_line_from('associate.analytic.line.from')
