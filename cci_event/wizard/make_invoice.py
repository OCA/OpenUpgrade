##############################################################################
#
# Copyright (c) 2005-2006 TINY SPRL. (http://tiny.be) All Rights Reserved.
#
# $Id: make_invoice.py 1070 2005-07-29 12:41:24Z nicoe $
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
import pooler

from osv import fields, osv
form = """<?xml version="1.0"?>
<form string="Create invoices">
    <newline />
    <field name="inv_created"/>
    <newline />
    <field name="inv_rejected"/>

</form>
"""
fields = {
      'inv_created': {'string':'Invoice Created', 'type':'char', 'readonly':True},
      'inv_rejected': {'string':'Invoice Rejected', 'type':'char', 'readonly':True},
          }

def _makeInvoices(self, cr, uid, data, context):
        invoices = {}
        invoice_ids = []
        create_ids=[]
        tax_ids=[]
        pool_obj=pooler.get_pool(cr.dbname)

        inv_create = 0
        inv_reject = 0
        list_inv = []
        obj_event_reg=pool_obj.get('event.registration')
        data_event_reg=obj_event_reg.browse(cr,uid,data['ids'])
        obj_lines=pool_obj.get('account.invoice.line')

        for reg in data_event_reg:
            if (not reg.tobe_invoiced) or (reg.invoice_id) or (reg.check_mode) or (not reg.check_ids):
                inv_reject = inv_reject + 1
                continue
            inv_create = inv_create + 1
            value=obj_lines.product_id_change(cr, uid, [], reg.event_id.product_id.id,uom =False, partner_id=reg.partner_invoice_id.id)

            if not reg.event_id.product_id:
                raise wizard.except_wizard('Warning !', 'No Product defined in the Event ')
            if not reg.partner_address_id:
                raise wizard.except_wizard('Warning !', 'No "Partner Contact" defined on Registration ')
            if not reg.partner_invoice_id:
                raise wizard.except_wizard('Warning !', 'No "Partner to Invoice" defined on the Registration ')

            data_product=pool_obj.get('product.product').browse(cr,uid,[reg.event_id.product_id.id])
            a = reg.partner_invoice_id.property_account_receivable.id

            for tax in data_product[0].taxes_id:
                tax_ids.append(tax.id)
            inv_id =pool_obj.get('account.invoice.line').create(cr, uid, {
                    'name': reg.invoice_label,
                    'account_id':value['value']['account_id'],
                    'price_unit': reg.unit_price,# value['value']['price_unit'],
                    'quantity': reg.nb_register,
                    'discount': False,
                    'uos_id': value['value']['uos_id'],
                    'product_id':reg.event_id.product_id.id,
                    'invoice_line_tax_id': [(6,0,tax_ids)],
                    'note':False,
            })
            create_ids.append(inv_id)

            inv = {
                'name': reg.invoice_label,
                'origin': reg.invoice_label,
                'type': 'out_invoice',
                'reference': False,
                'account_id': reg.partner_invoice_id.property_account_receivable.id,
                'partner_id': reg.partner_invoice_id.id,
                'address_invoice_id':reg.partner_address_id.id,
                'address_contact_id':reg.partner_address_id.id,
                'invoice_line': [(6,0,create_ids)],
                'currency_id' :reg.partner_invoice_id.property_product_pricelist.currency_id.id,# 1,
                'comment': "",
                'payment_term':reg.partner_invoice_id.property_payment_term.id,
            }

            inv_obj = pool_obj.get('account.invoice')
            inv_id = inv_obj.create(cr, uid, inv)
            list_inv.append(inv_id)
            obj_event_reg.write(cr, uid,data['ids'], {'invoice_id' : inv_id})

            if (not reg.tobe_invoiced) or reg.check_mode or (not reg.check_ids):
                pass
                #raise wizard.except_wizard('Warning !', 'This registration should not be invoiced ')
            if reg.invoice_id:
                pass
                #raise wizard.except_wizard('Warning !', 'This registration already has an invoice linked ')
        return {'inv_created' : str(inv_create) , 'inv_rejected' : str(inv_reject) , 'invoice_ids':  list_inv}

class make_invoice(wizard.interface):
    def _list_invoice(self, cr, uid, data, context):
        return {
            'domain': "[('id','in', ["+','.join(map(str,data['form']['invoice_ids']))+"])]",
            'name': 'Invoices',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'account.invoice',
            'view_id': False,
            'context': "{'type':'out_invoice'}",
            'type': 'ir.actions.act_window'
        }
    states = {
        'init' : {
               'actions' : [_makeInvoices],
               'result': {'type': 'form', 'arch': form, 'fields': fields, 'state':[('end','Ok'),('open','Open')]}
            },

        'open': {
            'actions': [],
            'result': {'type':'action', 'action':_list_invoice, 'state':'end'}
        }

    }

make_invoice("event.make_invoice")
