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
import pooler
import netsvc
from mx.DateTime import now

class profile_game_retail_phase_two(osv.osv):
    _name="profile.game.retail.phase2"
    _rec_name = 'state'
    _columns = {
                #sales manager
        'step1': fields.boolean('Confirm all DRAFT Purchase Order', readonly=True),
        'step2': fields.boolean('Validate Purchase Orders', readonly=True),
        'step3': fields.boolean('Confirm all draft supplier invoices', readonly=True),
        #logistic
        'step4': fields.boolean('Receive Products from Supplier', readonly=True),
        'step5': fields.boolean('Deliver Products to Customer', readonly=True),
         #financial
        'step6': fields.boolean('Pay all supplier invoices', readonly=True),
        'step7': fields.boolean('Validate all Draft customer invoices ', readonly=True),
        'step8': fields.boolean('Pay all open customer invoices', readonly=True),

        'state' :fields.selection([
            ('not running','Not Running'),
            ('confirm_po','Confirm Purchase Order'),
            ('validate_po','Validate Purchase Order'),
            ('confirm_supp_inv','Confirm Supplier Invoice'),
            ('receive','Receive Products'),
            ('run_sche','Run the Schedular'),
            ('confirm_pickings','confirm pickings'),
            ('supp_invoice_pay','Pay Supplier Invoice'),
            ('validate_customer_inv','Validate Customer Invoice'),
            ('cust_invoice_pay','Pay Customer Invoice'),
            ('done','Done'),], 'State', required=True,readonly=True),
        }
    _defaults = {
        'state': lambda *args: 'not running'
    }
    def continue_next_year(self, cr, uid, ids, context={}):
        partner_ids=self.pool.get('res.partner').search(cr,uid,[])
        prod_ids=self.pool.get('product.product').search(cr,uid,[])
        shop=self.pool.get('sale.shop').search(cr,uid,[])
        wf_service = netsvc.LocalService('workflow')
        for i in range(0,5):
            partner_addr = self.pool.get('res.partner').address_get(cr, uid, [partner_ids[i]],
                            ['invoice', 'delivery', 'contact'])
            pricelist = self.pool.get('res.partner').browse(cr, uid, partner_ids[i],
                            context).property_product_pricelist.id
            vals = {
                    'shop_id': shop[0],
                    'partner_id': partner_ids[i],
                    'pricelist_id': pricelist,
                    'partner_invoice_id': partner_addr['invoice'],
                    'partner_order_id': partner_addr['contact'],
                    'partner_shipping_id': partner_addr['delivery'],
                    'order_policy': 'postpaid',
                    'date_order': now(),
                }
            new_id = self.pool.get('sale.order').create(cr, uid, vals)
            value = self.pool.get('sale.order.line').product_id_change(cr, uid, [], pricelist,
                            prod_ids[i], qty=i, partner_id=partner_ids[i])['value']
            value['product_id'] = prod_ids[i]
            value['product_uom_qty']=i+100
            value['order_id'] = new_id
            self.pool.get('sale.order.line').create(cr, uid, value)
            wf_service.trg_validate(uid, 'sale.order', new_id, 'order_confirm', cr)
       # self.pool.get('mrp.procurement').run_scheduler(cr, uid, automatic=True, use_new_cursor=cr.dbname)
        return self.write(cr, uid, ids, {'state':'confirm_po'})

    def fields_view_get(self, cr, user, view_id=None, view_type='form', context=None, toolbar=False):
        res = super(profile_game_retail_phase_two, self).fields_view_get(cr, user, view_id, view_type, context, toolbar)
        res['arch'] = res['arch'].replace('role1', 'Fabien')
        res['arch'] = res['arch'].replace('role2', 'Fabien')
        res['arch'] = res['arch'].replace('role3', 'Fabien')
        return res
profile_game_retail_phase_two()