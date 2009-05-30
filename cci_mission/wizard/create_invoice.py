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

def _createInvoices(self, cr, uid, data, context={}):
    list_inv = []
    pool_obj = pooler.get_pool(cr.dbname)
    obj_dossier = pool_obj.get(data['model'])
    current_model=data['model']
    data_dossier = obj_dossier.browse(cr,uid,data['ids'])
    obj_lines=pool_obj.get('account.invoice.line')
    inv_create = 0
    inv_reject = 0
    inv_rej_reason = ""

    for data in data_dossier:
        context.update({'pricelist': data.order_partner_id.property_product_pricelist.id})
        list = []
        value = []
        dict = {}
        address_contact = False
        address_invoice = False
        create_ids = []
        if data.invoice_id:
            inv_reject = inv_reject + 1
            inv_rej_reason += "ID "+str(data.id)+": Already Has an Invoice Linked. \n"
            continue

        if not data.to_bill:
            inv_reject = inv_reject + 1
            inv_rej_reason += "ID "+str(data.id)+": Cannot Be Billed. \n"
            continue
        for add in data.order_partner_id.address:
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
            inv_rej_reason += "ID "+str(data.id)+": No Partner Address Defined on Billed Customer. \n"
            continue

        context.update({'date':data.date})
        inv_create = inv_create + 1
        for lines in data.product_ids :

            val = {}
            val['value']={}
            val['value'].update({'name':lines.name})
            val['value'].update({'account_id':lines.account_id.id})
            val['value'].update({'product_id' : lines.product_id.id })
            val['value'].update({'quantity' : lines.quantity })
            val['value'].update({'uos_id':lines.uos_id.id})
            val['value'].update({'price_unit':lines.price_unit})

            value.append(val)

        list.append(data.type_id.original_product_id.id)
        dict['original'] = data.type_id.original_product_id.id
        list.append(data.type_id.copy_product_id.id)
        dict['copy'] = data.type_id.copy_product_id.id
        fpos = data.order_partner_id.property_account_position and data.order_partner_id.property_account_position.id or False
        for prod_id in list:
            val = obj_lines.product_id_change(cr, uid, [], prod_id,uom =False, partner_id=data.order_partner_id.id, fposition_id=fpos)
            val['value'].update({'product_id' : prod_id })

            force_member=force_non_member=False
            if current_model=='cci_missions.legalization':
                if data.member_price==1:
                    force_member=True
                else:
                    force_non_member=True
            context.update({'partner_id':data.order_partner_id})
            context.update({'force_member':force_member})
            context.update({'force_non_member':force_non_member})
            context.update({'value_goods':data.goods_value})
            context.update({'date':data.date})

            price=pool_obj.get('product.product')._product_price(cr, uid, [prod_id], False, False, context)
            val['value'].update({'price_unit':price[prod_id]})

            if prod_id == dict['original']:
                val['value'].update({'quantity' : data.quantity_original })
            else:
                val['value'].update({'quantity' : data.quantity_copies})
            value.append(val)

        for val in value:
            if val['value']['quantity']>0.00:
                tax_on_line = []
                if val['value']['product_id'] != False:
                    tax_on_line = pool_obj.get('product.product').browse(cr,uid,val['value']['product_id']).taxes_id
                    inv_id =pool_obj.get('account.invoice.line').create(cr, uid, {
                        'name': val['value']['name'],
                        'account_id':val['value']['account_id'],
                        'price_unit': val['value']['price_unit'],
                        'quantity': val['value']['quantity'],
                        'discount': False,
                        'uos_id': val['value']['uos_id'],
                        'product_id':val['value']['product_id'],
                        'invoice_line_tax_id': [(6,0,tax_on_line)],
                        'note':data.text_on_invoice,
                    })
                else:
                    raise osv.except_osv('Input Error!','No Product Chosen')
                create_ids.append(inv_id)
        inv = {
            'name': data.name,
            'origin': data.name,
            'type': 'out_invoice',
            'reference': False,
            'account_id': data.order_partner_id.property_account_receivable.id,
            'partner_id': data.order_partner_id.id,
            'address_invoice_id':address_invoice,
            'address_contact_id':address_contact,
            'invoice_line': [(6,0,create_ids)],
            'currency_id' :data.order_partner_id.property_product_pricelist.currency_id.id,# 1,
            'comment': data.text_on_invoice,
            'payment_term':data.order_partner_id.property_payment_term.id,
            'fiscal_position': data.order_partner_id.property_account_position.id
            }
        price = data.total
        inv_obj = pool_obj.get('account.invoice')
        inv_id = inv_obj.create(cr, uid, inv)
        list_inv.append(inv_id)
        wf_service = netsvc.LocalService('workflow')
        wf_service.trg_validate(uid, current_model, data.id, 'invoiced', cr)

        obj_dossier.write(cr, uid,data.id, {'invoice_id' : inv_id, 'invoiced_amount':price})

    return {'inv_created' : str(inv_create) , 'inv_rejected' : str(inv_reject) , 'invoice_ids':  list_inv, 'inv_rej_reason': inv_rej_reason}


class create_invoice(wizard.interface):
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
            'result' : {'type' : 'form' ,   'arch' : form,'fields' : fields,'state' : [('end','Ok'),('open','Open Invoice')]}
        },
        'open': {
            'actions': [],
            'result': {'type':'action', 'action':_open_invoice, 'state':'end'}
        }
    }

create_invoice("mission.create_invoice")
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

