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
from osv import fields, osv
import time
from tools import config
import netsvc
import wizard

class ecommerce_saleorder(osv.osv):

    _name = 'ecommerce.saleorder'
    _description = 'ecommerce saleorder'
    _columns = {
        'name': fields.char('Order Reference', size=64, required=True),
        'date_order': fields.date('Date Ordered', required=True),
        'epartner_id': fields.many2one('ecommerce.partner', 'Ecommerce Partner', required=True),
        'epartner_add_id': fields.many2one('ecommerce.partner.address', 'Contact Address'),
        'epartner_shipping_id': fields.many2one('ecommerce.partner.address', 'Shipping Address'),
        'epartner_invoice_id': fields.many2one('ecommerce.partner.address', 'Invoice Address'),
        'pricelist_id': fields.many2one('product.pricelist', 'Pricelist', required=True),
        'web_id': fields.many2one('ecommerce.shop', 'Web Shop', required=True),
        'orderline_ids': fields.one2many('ecommerce.order.line', 'order_id', 'Order Lines'),
        'order_id': fields.many2one('sale.order', 'Sale Order'),
        'note': fields.text('Notes'),
    }
    _defaults = {
        'name': lambda obj, cr, uid, context: obj.pool.get('ir.sequence').get(cr, uid, 'ecommerce.saleorder'),
        'date_order': lambda *a: time.strftime('%Y-%m-%d'),
        'epartner_invoice_id': lambda self, cr, uid, context: context.get('partner_id', False) and self.pool.get('ecommerce.partner').address_get(cr, uid, [context['partner_id']], adr_pref=['invoice'])['invoice'],
        'epartner_add_id': lambda self, cr, uid, context: context.get('partner_id', False) and  self.pool.get('ecommerce.partner').address_get(cr, uid, [context['partner_id']], adr_pref=['contact'])['contact'],
        'epartner_shipping_id': lambda self, cr, uid, context: context.get('partner_id', False) and self.pool.get('ecommerce.partner').address_get(cr, uid, [context['partner_id']], adr_pref=['delivery'])['deliver']
    }

    def order_create_function(self, cr, uid, ids, context={}):

        get_ids = []
        for order in self.browse(cr, uid, ids, context):
            if not (order.epartner_id and order.epartner_invoice_id and order.epartner_shipping_id):
                raise osv.except_osv('No addresses !', 'You must assign addresses before creating the order.')

            res_prt = self.pool.get('res.partner')
            prt_id = res_prt.search(cr, uid, [('name', '=', order.epartner_id.name)])
            res = res_prt.read(cr, uid, prt_id, [], context)
            res_categ = self.pool.get('res.partner.category')
            search_categ = res_categ.search(cr, uid, [('name', '=', 'Customer')])

            if res:
                partner_id = res[0]['id']
                
            if not prt_id:
                partner_id = self.pool.get('res.partner').create(cr, uid, {
                    'name': order.epartner_id.name,
                    'lang':order.epartner_id.lang,
                    'category_id': [(6, 0, search_categ)]
                   })
                for addr_type in order.epartner_id.address_ids:
                    addid = self.pool.get('res.partner.address').create(cr, uid, {
                    'name': addr_type.username,
                    'type':addr_type.type,
                    'street':addr_type.street,
                    'street2':addr_type.street2,
                    'partner_id':partner_id,
                    'zip':addr_type.zip,
                    'city':addr_type.city,
                    'state_id':addr_type.state_id.id,
                    'country_id':addr_type.country_id.id,
                    'email':addr_type.email,
                    'phone':addr_type.phone,
                    'fax':addr_type.fax,
                    'mobile':addr_type.mobile
                })
            
            address_contact = False
            address_invoice = False
            address_delivery = False
            
            data_partner = res_prt.browse(cr, uid, partner_id)
            for tmp_addr_var in data_partner.address:
                if tmp_addr_var.type == 'contact':
                    address_contact = tmp_addr_var.id

                if tmp_addr_var.type == 'invoice':
                    address_invoice = tmp_addr_var.id

                if tmp_addr_var.type == 'delivery':
                    address_delivery = tmp_addr_var.id

                if (not address_contact) and (tmp_addr_var.type == 'default'):
                    address_contact = tmp_addr_var.id

                if (not address_invoice) and (tmp_addr_var.type == 'default'):
                    address_invoice = tmp_addr_var.id

                if (not address_delivery) and (tmp_addr_var.type == 'default'):
                    address_delivery = tmp_addr_var.id

            if (not address_contact) or (not address_invoice) or (not address_delivery):
                raise osv.except_osv('Error', 'Please Enter Default Address!')

            pricelist_id = order.pricelist_id.id
            order_lines = []
            for line in order.orderline_ids:
                val = {
                    'name': line.name,
                    'product_uom_qty': line.product_qty,
                    'product_id': line.product_id.id,
                    'product_uom': line.product_uom_id.id,
                    'price_unit': line.price_unit,
                }
                # fiscal position should be check....
                obj_so_line = self.pool.get('sale.order.line')
                val_new = obj_so_line.product_id_change(cr, uid, None, pricelist_id, line.product_id.id, line.product_qty, line.product_uom_id.id, name=line.name, partner_id=partner_id, fiscal_position=False)['value']
                del val_new['price_unit']
                del val_new['th_weight']
                val_new['product_uos'] = 'product_uos' in val_new and val_new['product_uos'] and val_new['product_uos'][0] or False
                val.update( val_new )
                val['tax_id'] = 'tax_id' in val and [(6, 0, val['tax_id'])] or False
                order_lines.append((0, 0, val))

            obj_shop = self.pool.get('ecommerce.shop')
            search_shop_id = obj_shop.browse(cr, uid, order.web_id.id)
            order_id = self.pool.get('sale.order').create(cr, uid, {
                'name': order.name,
                'shop_id': search_shop_id.shop_id.id,
                'user_id': uid,
                'note': order.note or '',
                'partner_id': partner_id,
                'partner_invoice_id':address_invoice,
                'partner_order_id':address_contact,
                'partner_shipping_id':address_delivery,
                'pricelist_id': order.pricelist_id.id,
                'order_line':order_lines,
                'order_policy': 'manual',
                'fiscal_position': data_partner.property_account_position and data_partner.property_account_position.id or False
            })
            self.write(cr, uid, ids, {'order_id':order_id})
            get_ids.extend(ids)
            get_ids.append(int(order_id))

        return get_ids

    def address_set(self, cr, uid, ids):

        done = []
        for order in self.browse(cr, uid, ids):
            for a in [order.epartner_shipping_id.id, order.epartner_invoice_id.id]:
                if a not in done:
                    done.append(a)
                    self.pool.get('ecommerce.partner').address_set(cr, uid, [a])
            self.write(cr, uid, [order.id], {
                'partner_shipping_id': order.epartner_invoice_id.address_id.id,
                'partner_id': order.epartner_invoice_id.address_id.partner_id.id,
                'partner_invoice_id': order.epartner_shipping_id.address_id.id
           })
        return True

    def onchange_epartner_id(self, cr, uid, ids, part):

        if not part:
            return {'value':{'epartner_invoice_id': False, 'epartner_shipping_id':False, 'epartner_add_id':False}}
        addr = self.pool.get('ecommerce.partner').address_get(cr, uid, [part], adr_pref=['delivery', 'invoice', 'contact'])
        return {'value': {'epartner_invoice_id': addr['invoice'], 'epartner_add_id': addr['contact'], 'epartner_shipping_id': addr['delivery']}}

    def confirm_sale_order(self, cr, uid, so_ids, email_id, shipping_charge, context={}):

        wf_service = netsvc.LocalService("workflow")
        ids = []
        inv_id = []
        datas = {}
        ids.append(so_ids)

        create_wf = self.order_create_function(cr, uid, ids, context={})
        sale_orderid = create_wf[1]
        wf_service.trg_validate(uid, 'sale.order', sale_orderid, 'order_confirm', cr)
        wf_service.trg_validate(uid, 'sale.order', sale_orderid, 'manual_invoice', cr)
        cr.commit()
        get_data = self.pool.get('sale.order').browse(cr, uid, sale_orderid)
        if(get_data.invoice_ids):
            invoice_id = get_data.invoice_ids[0].id
        else:
            raise osv.except_osv('Error', 'Yet Not Create Invoice!')

        wf_service.trg_validate(uid, 'account.invoice', invoice_id, 'invoice_open', cr)
        inv_id.append(invoice_id)

        acc_journal = self.pool.get('account.journal')
        journal_id = acc_journal.search(cr, uid, [('type', '=', 'cash'), ('code', '=', 'BNK')])

        journal = acc_journal.browse(cr, uid, journal_id, context)
        acc_id = journal[0].default_credit_account_id and journal[0].default_credit_account_id.id
        if not acc_id:
            raise wizard.except_wizard(_('Error !'), _('Your journal must have a default credit and debit account.'))
        period_id = self.pool.get('account.period').find(cr, uid)
        if not len(period_id):
            return dict.fromkeys(ids, 0.0)
        period_id = period_id[0]

        writeoff_account_id = False
        writeoff_journal_id = False
        entry_name = 'from ecom'

        acc_invoice_obj = self.pool.get('account.invoice')
        acc_invoice_obj.pay_and_reconcile(cr, uid, inv_id,
        get_data.amount_total, acc_id, period_id, journal_id[0], writeoff_account_id,
        period_id, writeoff_journal_id, context, entry_name)

        datas = {'model': 'account.invoice', 'id': invoice_id, 'report_type': 'pdf'}
        obj = netsvc.LocalService('report.'+'account.invoice.ecom')
        context = {'price': shipping_charge}
        (result, format) = obj.create(cr, uid, inv_id, datas, context)

        subject = str('Send Invoice')
        body = str('Dear  Subscriber,' + '\n'+'\n' +
                   'Your Payment Process finish..'+'\n' +
                   'Your invoice send it to you.' + '\n' + '\n' +'\n' +
                   'Thank you for using Ecommerce!' + '\n' +
                   'The Ecommerce Team')

        data = self.pool.get('ecommerce.partner')
        data.ecommerce_sendmail(cr, uid, email_id, subject, body, attachment=result, context={})

        return dict(inv_id=invoice_id, so_id=sale_orderid)

ecommerce_saleorder()

class ecommerce_order_line(osv.osv):
    _name = 'ecommerce.order.line'
    _description = 'ecommerce order line'
    _columns = {
        'name': fields.char('Description', size=64, required=True),
        'product_qty': fields.float('Quantity', digits=(16,2), required=True),
        'order_id': fields.many2one('ecommerce.saleorder', 'eOrder Ref'),
        'product_id': fields.many2one('product.product', 'Product', domain=[('sale_ok','=',True)], change_default=True),
        'product_uom_id': fields.many2one('product.uom', 'Product UOM',required=True),
        'price_unit': fields.float('Unit Price',digits=(16, int(config['price_accuracy'])), required=True),
    }
    
    def onchange_product(self, cr, uid, ids, product_id):

        product_obj = self.pool.get('product.product')
        if not product_id:
            return {'value': {'name': False, 'product_uom_id': False, 'price_unit':False}}
        else:
            product = product_obj.browse(cr, uid, product_id)
            return {'value': {'name': product.product_tmpl_id.name, 'product_uom_id': product.product_tmpl_id.uom_id.id,
                               'price_unit': product.lst_price}}
        
ecommerce_order_line()


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

