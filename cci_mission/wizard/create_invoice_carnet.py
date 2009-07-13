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
    obj_carnet = pool_obj.get('cci_missions.ata_carnet')
    data_carnet = obj_carnet.browse(cr,uid,data['ids'])
    obj_lines=pool_obj.get('account.invoice.line')
    inv_create = 0
    inv_reject = 0
    inv_rej_reason = ""
    list_inv = []

    for carnet in data_carnet:
        context.update({'pricelist': carnet.partner_id.property_product_pricelist.id})
        list = []
        value = []
        address_contact = False
        address_invoice = False
        create_ids = []
        if carnet.invoice_id:
            inv_reject = inv_reject + 1
            inv_rej_reason += "ID "+str(carnet.id)+": Already Has an Invoice Linked \n"
            continue

        context.update({'date':carnet.creation_date})
        list.append(carnet.type_id.original_product_id.id)
        list.append(carnet.type_id.copy_product_id.id)
        list.append(carnet.warranty_product_id.id)
        fpos = carnet.partner_id.property_account_position and carnet.partner_id.property_account_position.id or False
        for product_line in carnet.product_ids:#extra Products
            val = obj_lines.product_id_change(cr, uid, [], product_line.product_id.id,uom =False, partner_id=carnet.partner_id.id, fposition_id=fpos)
            val['value'].update({'product_id' : product_line.product_id.id })
            val['value'].update({'quantity' : product_line.quantity })
            val['value'].update({'price_unit':product_line.price_unit})
            value.append(val)

        for add in carnet.partner_id.address:
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
            inv_rej_reason += "ID "+str(carnet.id)+": No Partner Address Defined on Partner \n"
            continue
        inv_create = inv_create + 1
        count=0
        for prod_id in list:
            count += 1
            val = obj_lines.product_id_change(cr, uid, [], prod_id,uom =False, partner_id=carnet.partner_id.id, fposition_id=fpos)
            val['value'].update({'product_id' : prod_id })
            if count==2:
                qty_copy=carnet.initial_pages
                if qty_copy<0:
                    qty_copy=0
                val['value'].update({'quantity' : qty_copy })
            else:
                val['value'].update({'quantity' : 1 })
            force_member=force_non_member=False
            if carnet.member_price==1:
                force_member=True
            else:
                force_non_member=True
            context.update({'partner_id':carnet.partner_id})
            context.update({'force_member':force_member})
            context.update({'force_non_member':force_non_member})
            context.update({'value_goods':carnet.goods_value})
            context.update({'double_signature':carnet.double_signature})
            context.update({'date':carnet.creation_date})
            context.update({'emission_date':carnet.creation_date})

            price=pool_obj.get('product.product')._product_price(cr, uid, [prod_id], False, False, context)
            val['value'].update({'price_unit':price[prod_id]})

            value.append(val)
        for val in value:
            if val['value']['quantity']>0.00:
                inv_id =pool_obj.get('account.invoice.line').create(cr, uid, {
                        'name': val['value']['name'], #carnet.name
                        'account_id':val['value']['account_id'],
                        'price_unit': val['value']['price_unit'],
                        'quantity': val['value']['quantity'],
                        'discount': False,
                        'uos_id': val['value']['uos_id'],
                        'product_id':val['value']['product_id'],
                        'invoice_line_tax_id': [(6,0,val['value']['invoice_line_tax_id'])],
                        'note':'',
                })
                create_ids.append(inv_id)
        inv = {
                'name': carnet.name,
                'origin': carnet.name,
                'type': 'out_invoice',
                'reference': False,
                'account_id': carnet.partner_id.property_account_receivable.id,
                'partner_id': carnet.partner_id.id,
                'address_invoice_id':address_invoice,
                'address_contact_id':address_contact,
                'invoice_line': [(6,0,create_ids)],
                'currency_id' :carnet.partner_id.property_product_pricelist.currency_id.id,# 1,
                'comment': '',
                'payment_term':carnet.partner_id.property_payment_term.id,
                'fiscal_position': carnet.partner_id.property_account_position.id
            }

        inv_obj = pool_obj.get('account.invoice')
        inv_id = inv_obj.create(cr, uid, inv)
        list_inv.append(inv_id)
        wf_service = netsvc.LocalService('workflow')
        wf_service.trg_validate(uid, 'cci_missions.ata_carnet', carnet.id, 'created', cr)
        obj_carnet.write(cr, uid,[carnet.id], {'invoice_id' : inv_id})

    return {'inv_created' : str(inv_create),'inv_rejected' : str(inv_reject)  ,'invoice_ids':  list_inv , 'inv_rej_reason': inv_rej_reason }

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
            'result' : {'type' : 'form' ,   'arch' : form,
                    'fields' : fields,
                    'state' : [('end','Ok'),('open','Open Invoice')]}
                    },
        'open': {
            'actions': [],
            'result': {'type':'action', 'action':_open_invoice, 'state':'end'}
                }
            }
create_invoice("mission.create_invoice_carnet")
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

