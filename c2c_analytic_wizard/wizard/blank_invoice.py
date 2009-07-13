# -*- encoding: utf-8 -*-
##############################################################################
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
import pooler
import time


class invoice_create(wizard.interface):
    """Create an invoice based on selected AA"""
    def _get_accounts(self, cr, uid, data, context):
        """init default account """

        if not len(data['ids']):
            return {}
        return {'accounts': data['ids']}

    def _do_create(self, cr, uid, data, context):
        pool = pooler.get_pool(cr.dbname)
        projects_ids = data['form']['accounts'][0][2]
        invoices = []
        proj_obj = pool.get('account.analytic.account')
        try : 
            for project in proj_obj.browse(cr, uid, projects_ids, context):
                partner = project.partner_id
                if (not partner) or not (project.pricelist_id):
                    raise wizard.except_wizard(
                                        'Analytic account or project incomplete', 
                                        """Please fill in the pricelist field in the
analytic account:
%s 
And the partner 
in project:
%s""" % (project.name,project.name)
                                                )
                if project.contact_id:
                    inv_contact = project.contact_id.id
                else:
                    inv_contact = pool.get('res.partner').address_get(
                                                            cr, 
                                                            uid, 
                                                            [project.partner_id.id], 
                                                            adr_pref=['invoice']
                                                        )['invoice']
                                
                account_payment_term_obj = pool.get('account.payment.term')
                date_due=False
                if partner.property_payment_term:
                    pterm_list= account_payment_term_obj.compute(
                                                     cr, 
                                                     uid,
                                                     partner.property_payment_term.id, 
                                                     value=1,
                                                     date_ref=time.strftime('%Y-%m-%d')
                                                    )
                    if pterm_list:
                        pterm_list = [line[0] for line in pterm_list]
                        pterm_list.sort()
                        date_due = pterm_list[-1]
                        
                address_contact_id = pool.get('res.partner').\
                    address_get(
                                    cr, 
                                    uid, 
                                    [project.partner_id.id], 
                                    adr_pref=['contact']
                                )
                # Attention au type de facture !
                curr_invoice = {
                    'name': time.strftime('%D')+' - '+project.name,
                    'partner_id': project.partner_id.id,
                    'address_contact_id': address_contact_id['contact'],
                    'address_invoice_id': inv_contact,
                    'payment_term': partner.property_payment_term.id or False,
                    'account_id': partner.property_account_receivable.id,
                    'currency_id': project.pricelist_id.currency_id.id,
                    'type':'out_invoice',
                    'date_due': date_due,
                }
                
                
                last_invoice = pool.get('account.invoice').create(cr, uid, curr_invoice)
                invoices.append(last_invoice)
                        
            cr.execute(
                            "select id,name from ir_ui_view \
                            where model= 'account.invoice' \
                            and name = 'account.invoice.form.inherit'"
                        )
            view_res = cr.fetchone()

            return {
                'domain': "[('id','in', ["+','.join(map(str,invoices))+"])]",
                'name': 'Invoices',
                'view_type': 'form',
                'view_mode': 'tree',
                'res_model': 'account.invoice',
                'view_id': view_res,
                'context': "{'type':'out_invoice'}",
                'type': 'ir.actions.act_window',
                'res_id': invoices
            }
        except Exception, e:
            raise wizard.except_wizard(
                                        'Error !', 
                                         str(e.name)+' '+str(e.value)
                                      )
        
    _create_form = """<?xml version="1.0"?>
    <form string="Create blank invoice">
        <separator string="Choose analytic accounts 
        you want to create a blank invoice" colspan="4"/>
        <field name="accounts" colspan="4" >
        </field>
    </form>"""

    _create_fields = {
        'accounts': {
                        'string':'Analytic accounts', 
                        'type':'many2many', 
                        'required':'true', 
                        'relation':'account.analytic.account'
                    },
    }

    states = {
        'init' : {
            'actions' : [_get_accounts], 
            'result' : {
                        'type':'form', 
                        'arch':_create_form, 
                        'fields':_create_fields, 
                        'state': [
                                    ('end','Cancel'),
                                    ('create','Create blank invoice')
                                ]
                        },
        },
        'create' : {
            'actions' : [],
            'result' : {
                            'type':'action',
                            'action':_do_create,
                            'state':'end'
                        },
        },
    }
invoice_create('blank.invoice')
