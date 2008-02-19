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


def _makeInvoices(self, cr, uid, data, context):
        invoices = {}
        invoice_ids = []
        create_ids=[]
        tax_ids=[]

        pool_obj=pooler.get_pool(cr.dbname)

        obj_event_reg=pool_obj.get('event.registration')
        data_event_reg=obj_event_reg.browse(cr,uid,data['ids'])

        obj_lines=pool_obj.get('account.invoice.line')

        value=obj_lines.product_id_change(cr, uid, [], data_event_reg[0].event_id.product_id.id,uom =False, partner_id=data_event_reg[0].partner_invoice_id.id)

        data_product=pool_obj.get('product.product').browse(cr,uid,[data_event_reg[0].event_id.product_id.id])
        a = data_event_reg[0].partner_invoice_id.property_account_receivable.id

        for tax in data_product[0].taxes_id:
            tax_ids.append(tax.id)

        inv_id =pool_obj.get('account.invoice.line').create(cr, uid, {
                'name': data_event_reg[0].name,
                'account_id':value['value']['account_id'],
                'price_unit': value['value']['price_unit'],
                'quantity': data_event_reg[0].nb_register,
                'discount': False,
                'uos_id': value['value']['uos_id'],
                'product_id':data_event_reg[0].event_id.product_id.id,
                'invoice_line_tax_id': [(6,0,tax_ids)],
                'note':False,
        })
        create_ids.append(inv_id)

        inv = {
            'name': data_event_reg[0].name,
            'origin': data_event_reg[0].name,
            'type': 'out_invoice',
            'reference': False,#"P%dSO%d"%(loan.partner_id.id,loan.id),
            'account_id': data_event_reg[0].partner_invoice_id.property_account_receivable.id,
            'partner_id': data_event_reg[0].partner_invoice_id.id,
            'address_invoice_id': data_event_reg[0].partner_address_id.id,
            'address_contact_id': data_event_reg[0].partner_address_id.id,
            'invoice_line': [(6,0,create_ids)],
            'currency_id' : data_event_reg[0].partner_invoice_id.property_product_pricelist.currency_id.id,# 1,
            'comment': "",
            'payment_term': data_event_reg[0].partner_invoice_id.property_payment_term.id,
        }

        inv_obj = pool_obj.get('account.invoice')
        inv_id = inv_obj.create(cr, uid, inv)
        return {}


class make_invoice(wizard.interface):
    states = {
        'init' : {
            'actions' : [_makeInvoices],
            'result' : {'type' : 'state',
                    'state' : 'end'}
        },

    }
make_invoice("event.make_invoice")
