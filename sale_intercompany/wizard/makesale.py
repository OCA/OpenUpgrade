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

from mx.DateTime import now

import wizard
import netsvc
import ir
import pooler

class make_sale(wizard.interface):

    def _selectPartner(self, cr, uid, data, context):
        case_obj = pooler.get_pool(cr.dbname).get('crm.case')
        case = case_obj.read(cr, uid, data['ids'], ['partner_id'])
        return {'partner_id': case[0]['partner_id']}

    def _makeOrder(self, cr, uid, data, context):
        pool = pooler.get_pool(cr.dbname)
        purchase_obj = pool.get('purchase.order')
        sale_obj = pool.get('sale.order')

        shop_obj = pool.get('sale.shop')
        shop_id = shop_obj.search(cr, uid, [])[0]

        partner_obj = pool.get('res.partner')
        sale_line_obj = pool.get('sale.order.line')


        new_ids = []

        user = pool.get('res.users').browse(cr, uid, uid)
        partner_id = user.company_id.partner_id.id
        partner_addr = partner_obj.address_get(cr, uid, [partner_id],
                ['invoice', 'delivery', 'contact'])
        default_pricelist = partner_obj.browse(cr, uid, partner_id,
                    context).property_product_pricelist.id
        fpos = partner_obj.browse(cr, uid, partner_id,
                    context).property_account_position
        fpos_id = fpos and fpos.id or False

        for purchase in purchase_obj.browse(cr, uid, data['ids']):
            vals = {
                'origin': 'PO:%s' % str(purchase.name),
                'picking_policy': 'direct',
                'shop_id': shop_id,
                'partner_id': partner_id,
                'pricelist_id': default_pricelist,
                'partner_invoice_id': partner_addr['invoice'],
                'partner_order_id': partner_addr['contact'],
                'partner_shipping_id': partner_addr['delivery'],
                'order_policy': 'manual',
                'date_order': now(),
                'fiscal_position': fpos_id
            }
            new_id = sale_obj.create(cr, uid, vals)
            fpos = user.company_id.partner_id.property_account_position and user.company_id.partner_id.property_account_position.id or False
            for line in purchase.order_line:
                value = sale_line_obj.product_id_change(cr, uid, [], default_pricelist,
                        line.product_id.id, qty=line.product_qty, partner_id=partner_id, fiscal_position=fpos)['value']
                value['price_unit'] = line.price_unit
                value['product_id'] = line.product_id.id
                value['product_uos'] = value.get('product_uos', [False,False])[0]
                value['product_uom_qty'] = line.product_qty
                value['order_id'] = new_id
                sale_line_obj.create(cr, uid, value)

        return {}

    states = {
        'init': {
            'actions': [_makeOrder],
            'result': {'type': 'state', 'state': 'end'}
        }
    }

make_sale('purchase.order.interco')
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

