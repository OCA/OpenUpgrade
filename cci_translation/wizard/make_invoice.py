# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2008 Tiny SPRL (<http://tiny.be>). All Rights Reserved
#    $Id$
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

import wizard
import netsvc
import pooler

from osv import fields, osv
form = """<?xml version="1.0"?>
<form string="Create invoices">
    <field name="inv_created"/>
    <newline />
    <field name="inv_rejected"/>
    <newline />
    <field name="inv_rej_reason" width="400"/>

</form>
"""

fields = {
        'inv_created': {'string':'Invoice Created', 'type':'char', 'readonly':True},
        'inv_rejected': {'string':'Invoice Rejected', 'type':'char', 'readonly':True},
        'inv_rej_reason': {'string':'Error Messages', 'type':'text', 'readonly':True},
        }

def _createInvoices(self, cr, uid, data, context):
    pool_obj = pooler.get_pool(cr.dbname)
    obj_transfolder = pool_obj.get('translation.folder')
    data_transfolder = obj_transfolder.browse(cr,uid,data['ids'])
    obj_lines=pool_obj.get('account.invoice.line')
    inv_create = 0
    inv_reject = 0
    inv_rej_reason = ""
    list_inv = []

    for transfolder in data_transfolder:
        address_contact = False
        address_invoice = False
        create_ids = []
        if transfolder.invoice_id:
            inv_reject = inv_reject + 1
            inv_rej_reason += "ID "+str(transfolder.id)+": Already Has an Invoice Linked \n"
            continue

        if transfolder.state <> 'confirmed':
            inv_reject = inv_reject + 1
            inv_rej_reason += "ID "+str(transfolder.id)+": The Folder Isn't in 'Confirmed' State \n"
            continue

        for add in transfolder.partner_id.address:
            if add.type == 'contact':
                address_contact = add.id
            if add.type == 'invoice':
                address_invoice = add.id
            if (not address_contact) and (add.type == 'default'):
                address_contact = add.id
            if (not address_invoice) and (add.type == 'default'):
                address_invoice = add.id

        if not address_invoice:
            inv_reject = inv_reject + 1
            inv_rej_reason += "ID "+str(transfolder.id)+": No Partner Address Defined on Partner \n"
            continue
        inv_create = inv_create + 1

        translation_product_id = pool_obj.get('product.product').search(cr, uid, [('name', 'like', 'Translation Folder')])[0]
        fpos = transfolder.partner_id.property_account_position and transfolder.partner_id.property_account_position.id or False
        val = obj_lines.product_id_change(cr, uid, [], translation_product_id,uom =False, partner_id = transfolder.partner_id.id, fposition_id=fpos)

        note = ''
        cci_special_reference = False

        if transfolder.awex_eligible and transfolder.awex_amount > 0:
            note = 'AWEX intervention for a total of ' + str(transfolder.awex_amount)
            cci_special_reference = "translation.folder*" + str(transfolder.id)

        inv_id =pool_obj.get('account.invoice.line').create(cr, uid, {
            'name': val['value']['name'],
            'account_id': val['value']['account_id'],
            'price_unit': transfolder.base_amount,
            'quantity': 1,
            'discount': False,
            'uos_id': val['value']['uos_id'],
            'product_id': translation_product_id,
            'invoice_line_tax_id': [(6,0,val['value']['invoice_line_tax_id'])],
            'note': note,
            'cci_special_reference': cci_special_reference
        })
        inv = {
            'name': transfolder.name,
            'origin': transfolder.name,
            'type': 'out_invoice',
            'reference': False,
            'account_id': transfolder.partner_id.property_account_receivable.id,
            'partner_id': transfolder.partner_id.id,
            'address_invoice_id':address_invoice,
            'address_contact_id':address_contact,
            'invoice_line': [(6,0,[inv_id])],
            'currency_id' :transfolder.partner_id.property_product_pricelist.currency_id.id,
            'comment': '',
            'payment_term':transfolder.partner_id.property_payment_term.id,
            'fiscal_position': transfolder.partner_id.property_account_position.id
        }

        inv_obj = pool_obj.get('account.invoice')
        inv_id = inv_obj.create(cr, uid, inv)
        list_inv.append(inv_id)
        wf_service = netsvc.LocalService('workflow')
        wf_service.trg_validate(uid, 'translation.folder', transfolder.id, 'invoiced', cr)
        obj_transfolder.write(cr, uid,[transfolder.id], {'invoice_id' : inv_id})

    return {'inv_created' : str(inv_create),'inv_rejected' : str(inv_reject)  ,'invoice_ids':  list_inv , 'inv_rej_reason': inv_rej_reason }

class translation_create_invoice(wizard.interface):

    def _open_invoice(self, cr, uid, data, context):
        pool_obj = pooler.get_pool(cr.dbname)
        model_data_ids = pool_obj.get('ir.model.data').search(cr,uid,[('model','=','ir.ui.view'),('name','=','invoice_form')])
        resource_id = pool_obj.get('ir.model.data').read(cr,uid,model_data_ids,fields=['res_id'])[0]['res_id']

        return {
            'domain': "[('id','in', ["+','.join(map(str,data['form']['invoice_ids']))+"])]",
            'name': 'Invoices',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'account.invoice',
            'views': [(False,'tree'),(resource_id,'form')],
            'context': "{'type':'out_invoice'}",
            'type': 'ir.actions.act_window'
        }

    states = {
        'init' : {
            'actions' : [_createInvoices],
            'result' : {'type' : 'form' ,   'arch' : form,
                    'fields' : fields,
                    'state' : [('end','Ok'),('open','Open Invoice')]}
                    },
        'open': {
            'actions': [],
            'result': {'type':'action', 'action':_open_invoice, 'state':'end'}
                }
            }
translation_create_invoice("create_invoice_transfolder")
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

