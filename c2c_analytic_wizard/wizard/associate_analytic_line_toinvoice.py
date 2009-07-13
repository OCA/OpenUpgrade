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


class wiz_associate_analytic_line_toinvoice(wizard.interface):
    """ assign analytic line to invoice from invoice"""

    
    def _associate(self, cr, uid, data, context):
        """ fill the invoice_id filed on choosen AA lines """
    # If ids empty or more than one => raise error because, we can't associat to it 
        if not len(data['ids']):
            raise wizard.except_wizard(
                                        'Error !', 
                                        'No invoice selected !'
                                     )
        if len (data['ids'])>1:
            raise wizard.except_wizard(
                                        'Error !', 
                                        'You can not associate lines with more\
                                         than one invoice !'
                                    )
        try :
            pool = pooler.get_pool(cr.dbname)
            line_ids = data['form']['lines'][0][2]
            line_obj=pool.get('account.analytic.line')
            vals = {'invoice_id': data['ids'][0]}
            for line_id in line_ids:
                line_obj.write(
                                cr, 
                                uid,
                                line_id,
                                vals,
                                )
        except Exception, e:
            raise wizard.except_wizard(
                                        'Error !', 
                                         str(e.name)+' '+str(e.value)
                                      )

        return True
    

    _create_form = """<?xml version="1.0"?>
    <form string="Associate selected line to the invoice">
        <separator string="Choose AA. lines you want to invoice" colspan="4"/>
        <field name="lines" nolabel="1" colspan="4" 
            domain="[('invoice_id','=',False),('to_invoice','&lt;&gt;',False)]"/>
    </form>"""

    _create_fields = {
        'lines': {
                    'string':'Analytic Accounts Lines',
                    'type':'many2many', 
                    'required':'true',
                     'relation':'account.analytic.line'
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
wiz_associate_analytic_line_toinvoice('associate.analytic.line.toinvoice')
