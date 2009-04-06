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

class ecommerce_payment_method(osv.osv):
    
    _name = "ecommerce.payment.method"
    _description = "payment method"
    _columns = {
        'name': fields.char('Name', size=64, required=True),
        'shortcut': fields.char('Shortcut', size=64, required=True),
    }        
ecommerce_payment_method()

class ecommerce_creditcard(osv.osv):
    _name = "ecommerce.creditcard"
    _description = "Credit Cards"
    _columns = {
        'name': fields.char('Card Name', size=64, required=True),
        'code': fields.char('Code', size=28, required=True)
    }
ecommerce_creditcard()

class ecommerce_payment(osv.osv):
    
    _name = "ecommerce.payment"
    _description = "ecommerce payment"

    def _get_method(self, cursor, user, context=None):
        obj_payment = self.pool.get('ecommerce.payment.method')
        ids_method = obj_payment.search(cursor, user, [])
        data_method = obj_payment.read(cursor, user, ids_method,
                                        ['shortcut', 'name'], context)
        return [(r['shortcut'], r['name']) for r in data_method]
        
    _columns = {
        'name': fields.selection(_get_method, 'Payment Method', 
                                 size=64, required=True),
        'chequepay_to': fields.char('Account Owner', size=128, required=False),
        'street': fields.char('Street', size=128, required=False),
        'street2': fields.char('Street2', size=128, required=False),
        'zip': fields.char('Zip', change_default=True, size=24, required=False),
        'city': fields.char('City', size=128, required=False),
        'state_id': fields.many2one('res.country.state', 'State',
                                    required=False),
        'country_id': fields.many2one('res.country', 'Country', required=False),
        'biz_account': fields.char('Business E-mail Id', required=False, 
                                   size=128, help="Paypal business account Id."),
        'return_url': fields.char('Return URL', required=False, size=128,
                                   help="Return url which is set at the paypal account."),
        'cancel_url': fields.char('Cancel URL', required=False, size=128, 
                                  help="Cancel url which is set at the paypal account."),
        'transaction_dtl_ids': fields.one2many('ecommerce.payment.received','paypal_acc_id', 
                                'Transaction History', help="Transaction detail with the uniq transaction id."),
        'creditcard_ids': fields.many2many('ecommerce.creditcard', 'creditcard_method',
                                            'creditcards', 'ecommerce_creditcard', 'Credit Cards'),
        'acc_number': fields.char('Account Number', size=64, help="Bank account number"),
        'bic': fields.char('BIC number or SWIFT', size=64),
        'bank_name': fields.char('Bank Name', size=128)            
    }
ecommerce_payment()

class ecommerce_payment_received(osv.osv):
    
    _name = "ecommerce.payment.received"
    _description = "ecommerce payment received"
    _columns = {
        'transaction_id': fields.char('Transaction Id', size=128, readonly=True,
                                       help="Its Unique id which is generated from the paypal."),
        'saleorder_id': fields.many2one('sale.order', 'Sales Order'),
        'invoice_id': fields.many2one('account.invoice', 'Invoice'),
        'transaction_date': fields.date('Date Payment', required=True, 
                                        help="Transaction finish date."),
        'partner_id': fields.many2one('res.partner', 'Partner', required=True),
        'paypal_acc_id': fields.many2one('ecommerce.payment', 'Paypal Account', required=True)
    }
        
    _defaults = {
        'transaction_date': lambda *a: time.strftime('%Y-%m-%d')
    }
ecommerce_payment_received()

class ecommerce_shop(osv.osv):
        
    _name = "ecommerce.shop"
    _description = "ecommerce shop"
    _columns = {
        'name': fields.char('Name', size=256, required=True,
            help="Name of the shop which you are configure at website."),
        'company_id': fields.many2one('res.company', 'Company'),
        'shop_id': fields.many2one('sale.shop', 'Sale Shop', required=True),
 	    'payment_method_ids': fields.many2many('ecommerce.payment', 'shop_payment', 'shop_id',
                                                 'payment_id', 'Payment Methods', required=False),
        'category_ids': fields.one2many('ecommerce.category', 'web_id', 'Categories', translate=True,
            help="Add the product categories which you want to displayed on the website."),
        'currency_ids': fields.many2many('res.currency','currency_rel', 'currency', 'ecommerce_currency',
                                          'Currency', help="Add the currency options for the online customers."),
        'language_ids': fields.many2many('res.lang', 'lang_rel', 'language','ecommerce_lang', 'Language',
            help="Add the launguage options for the online customers."),
        'row_configuration': fields.integer('No. of Rows', 
                                            help="Add number of rows for products which you want to configure at website"),
        'column_configuration': fields.integer('No. of Columns', 
                                               help="Add number of columns for products which you want to configure at website"),
        'image_height': fields.integer('Height in Pixel', help="Add product image height in pixels."),
        'image_width': fields.integer('Width in Pixel', help="Add product image width in pixels."),
        'delivery_ids': fields.many2many('delivery.grid', 'delivery_rel', 'delivery', 'ecommrce_delivery',
                                          'Delivery', help="Add the carriers which you use for the shipping."),
        'search_ids': fields.many2many('ecommerce.search', 'search_rel', 'search', 'ecommrce_search_parameter', 
                                       'Search On', help="Add the search parameters which you are allow from the website." )
        } 

    _defaults = {
        'row_configuration': lambda *a: 3,
        'column_configuration': lambda *a: 3,
        'image_height': lambda *a: 30,
        'image_width': lambda *a:30
    }  
ecommerce_shop()

class ecommerce_category(osv.osv):
   
    _name = "ecommerce.category"
    _description = "ecommerce category"
    _columns = {
        'name': fields.char('E-commerce Category', size=64, required=True, 
                            help="Add the category name which you want to display at the website."),
        'web_id': fields.many2one('ecommerce.shop', 'Web Shop'),
        'category_id': fields.many2one('product.category', 'Tiny Category',
                                        help="It display the product which are under the openerp category."),
        'parent_category_id': fields.many2one('ecommerce.category','Parent Category'),
        'child_ids': fields.one2many('ecommerce.category', 'parent_category_id',
                                      string='Child Categories'), 
    }
ecommerce_category() 

       

