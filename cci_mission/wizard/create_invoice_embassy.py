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
import pooler
import netsvc
import time

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
    obj_embassy = pool_obj.get('cci_missions.embassy_folder')
    data_embassy = obj_embassy.browse(cr,uid,data['ids'])
    obj_lines=pool_obj.get('account.invoice.line')
    inv_create = 0
    inv_reject = 0
    inv_rej_reason = ""
    list_inv = []
    for embassy in data_embassy:
        address_contact = False
        address_invoice = False
        create_ids = []

        if embassy.state != 'open':
            inv_reject = inv_reject + 1
            inv_rej_reason += "ID "+str(embassy.id)+": Check State. Folder should be Open for Invoicing. \n"
            continue
        if embassy.invoice_id:
            inv_reject = inv_reject + 1
            inv_rej_reason += "ID "+str(embassy.id)+": Already Has an Invoice Linked. \n"
            continue
        if not embassy.partner_id:
            inv_reject = inv_reject + 1
            inv_rej_reason += "ID "+str(embassy.id)+": Embassy Folder Does not Have any Partner to Invoice. \n"
            continue
        for add in embassy.partner_id.address:
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
            inv_rej_reason += "ID "+str(embassy.id)+": No Partner Invoice Address Defined on Partner. \n"
            continue
        for line in embassy.embassy_folder_line_ids:
            tax_ids = []
            if line.tax_rate:
                tax_ids.append(line.tax_rate.id)
            cci_special_reference = False
            note = ''

            if line.awex_eligible and line.awex_amount > 0:
                note = 'AWEX intervention for a total of ' + str(line.awex_amount)
                cci_special_reference = "cci_missions.embassy_folder_line*" + str(line.id)

            inv_id =pool_obj.get('account.invoice.line').create(cr, uid, {
                    'name': line.name,
                    'account_id':line.account_id.id,
                    'price_unit': line.customer_amount,
                    'quantity': 1,
                    'discount': False,
                    'uos_id': False,
                    'product_id':False,
                    'invoice_line_tax_id': [(6,0,tax_ids)],
                    'note': note,
                    'cci_special_reference': cci_special_reference
            })
            create_ids.append(inv_id)
        inv = {
                'name': embassy.name,
                'origin': embassy.name,
                'type': 'out_invoice',
                'reference': embassy.customer_reference,
                'account_id': embassy.partner_id.property_account_receivable.id,
                'partner_id': embassy.partner_id.id,
                'address_invoice_id':address_invoice,
                'address_contact_id':address_contact,
                'invoice_line': [(6,0,create_ids)],
                'currency_id' :embassy.partner_id.property_product_pricelist.currency_id.id,# 1,
                'comment': embassy.invoice_note,
                'payment_term':embassy.partner_id.property_payment_term.id,
                'fiscal_position': embassy.partner_id.property_account_position.id
        }
        inv_create = inv_create + 1
        inv_obj = pool_obj.get('account.invoice')
        inv_id = inv_obj.create(cr, uid, inv)
        obj_embassy.write(cr, uid,embassy.id, {'invoice_id' : inv_id})
        list_inv.append(inv_id)
        obj_embassy.write(cr, uid,[embassy.id], {'state':'done','invoice_date': time.strftime('%Y-%m-%d %H:%M:%S')})
        wf_service = netsvc.LocalService('workflow')
        wf_service.trg_validate(uid, 'cci_missions.embassy_folder', embassy.id, 'done', cr)

    return {'inv_created' : str(inv_create) , 'inv_rejected' : str(inv_reject) , 'inv_rej_reason': inv_rej_reason , 'invoice_ids':  list_inv}

class create_invoice(wizard.interface):
    def _open_invoice(self, cr, uid, data, context):
        pool_obj = pooler.get_pool(cr.dbname)
        model_data_ids = pool_obj.get('ir.model.data').search(cr,uid,[('model','=','ir.ui.view'),('name','=','invoice_form')])
        resource_id = pool_obj.get('ir.model.data').read(cr,uid,model_data_ids,fields=['res_id'])[0]['res_id']
        val = {
            'domain': "[('id','in', ["+','.join(map(str,data['form']['invoice_ids']))+"])]",
            'name': 'Invoices',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'account.invoice',
            'views': [(False,'tree'),(resource_id,'form')],
            'context': "{'type':'out_invoice'}",
            'type': 'ir.actions.act_window'
        }
        return val

    states = {
        'init' : {
            'actions' : [_createInvoices],
            'result' : {
                'type' : 'form' ,
                'arch' : form,
                'fields' : fields,
                'state' : [('end','Ok'),('open','Open Invoice')]
            }
        },
        'open': {
            'actions': [],
            'result': {'type':'action', 'action':_open_invoice, 'state':'end'}
        }
    }

create_invoice("mission.create_invoice_embassy")
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

