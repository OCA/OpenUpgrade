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

from osv import fields,osv
from osv import orm
import time



class sale_order(osv.osv):
    _inherit = "sale.order"

    _columns = {
        'published_customer': fields.many2one('res.partner','Published Customer'),
        'advertising_agency': fields.many2one('res.partner','Advertising Agency'),
    }

    def onchange_published_customer(self, cursor, user, ids ,published_customer):
        data = {'advertising_agency':published_customer,'partner_id':published_customer,'partner_invoice_id': False, 'partner_shipping_id':False, 'partner_order_id':False}
        if published_customer:
            address = self.onchange_partner_id(cursor, user, ids, published_customer)
            data.update(address['value'])
        return {'value' : data}

    def onchange_advertising_agency(self, cursor, user, ids, ad_agency):
        data = {'partner_id':ad_agency,'partner_invoice_id': False, 'partner_shipping_id':False, 'partner_order_id':False}
        if ad_agency:
            address = self.onchange_partner_id(cursor, user, ids, ad_agency)
            data.update(address['value'])
        return {'value' : data}

sale_order()

class sale_advertising_issue(osv.osv):
    _name = "sale.advertising.issue"
    _description="Sale Advertising Issue"
    _columns = {
        'name': fields.char('Name', size=32, required=True),
        'issue_date': fields.date('Issue Date', required=True),
        'medium': fields.many2one('product.category','Medium', required=True),
        'state': fields.selection([('open','Open'),('close','Close')], 'State'),
        'default_note': fields.text('Default Note'),
    }
    _defaults = {
        'issue_date': lambda *a: time.strftime('%Y-%m-%d'),
        'state': lambda *a: 'open',
    }

sale_advertising_issue()

class sale_order_line(osv.osv):
    _inherit = "sale.order.line"
    _columns = {
        'layout_remark': fields.text('Layout Remark'),
        'adv_issue': fields.many2one('sale.advertising.issue','Advertising Issue'),
        'page_reference': fields.char('Reference of the Page', size=32),
        'from_date': fields.datetime('Start of Validity'),
        'to_date': fields.datetime('End of Validity'),
    }
sale_order_line()

class product_product(osv.osv):
    _inherit = "product.product"
    _columns = {
        'equivalency_in_A4': fields.float('A4 Equivalency',digits=(16,2)),
    }
product_product()

class sale_advertising_proof(osv.osv):
    _name = "sale.advertising.proof"
    _description="Sale Advertising Proof"
    _columns = {
        'name': fields.char('Name', size=32, required=True),
        'address_id':fields.many2one('res.partner.address','Delivery Address', required=True),
        'number': fields.integer('Number of Copies', required=True),
        'target_id': fields.many2one('sale.order','Target', required=True),
    }
    _defaults = {
        'number': lambda *a: 1,
    }
sale_advertising_proof()


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

