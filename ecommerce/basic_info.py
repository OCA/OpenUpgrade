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
from osv import fields , osv
import datetime
import time
import netsvc
import ir


class ecommerce_payment(osv.osv):
    
        _name = "ecommerce.payment"
        _description = "ecommerce payment configuration"
        _columns = {
            'name': fields.char('Cheque Payable to', size=256, required=True),
            'street': fields.char('Street', size=128, required=True),
            'street2': fields.char('Street2', size=128, required=True),
            'zip': fields.char('Zip', change_default=True, size=24, required=True),
            'city': fields.char('City', size=128, required=True),
            'state_id': fields.many2one("res.country.state", 'State', required=True),
            'country_id': fields.many2one('res.country', 'Country', required=True),
	    	'biz_account': fields.char('Your Business E-mail Id', required=True, size=128),
            'return_url' : fields.char('Return URL', required=True, size=128),
            'cancel_url' : fields.char('Cancel URL', required=True, size=128),
  			'transaction_detail' : fields.one2many('ecommerce.payment.received','paypal_acc', 'Transaction History')
             }
ecommerce_payment()

class ecommerce_payment_received(osv.osv):
    
        _name = "ecommerce.payment.received"
        _description = "ecommerce payment received"
        _columns = {
            'transaction_id': fields.char('Uniq Transaction Id', size=128, required=True),
            'saleorder_id' : fields.many2one('sale.order', 'Sale Order', required=True),
            'invoice_id' : fields.many2one('account.invoice', 'Invoice', required=True),
            'transaction_date' : fields.date('Date', required=True),
            'partner' : fields.many2one('res.partner', 'Partner', required=True),
            'paypal_acc' : fields.many2one('ecommerce.payment', 'Paypal Account', required=True)
            }
        
        _defaults = {
            'transaction_date': lambda *a: time.strftime('%Y-%m-%d')
        }
        
ecommerce_payment_received()

class ecommerce_shop(osv.osv):
        
    _name = "ecommerce.shop"
    _description = "ecommerce shop"
    _columns = {
        'name': fields.char('Name', size=256, required=True),
        'company_id': fields.many2one('res.company', 'Company'),
        'shop_id': fields.many2one('sale.shop', 'Sale Shop', required=True),
        'chequepay_to':fields.many2one('ecommerce.payment', 'Cheque Payable to', required=True),
        'category_ids': fields.one2many('ecommerce.category', 'web_id','Categories', translate=True),
        'products':fields.many2many('product.product','ecommerce_new_product_rel','product','ecommerce_product','Products',readonly=True),
        'currency_ids': fields.many2many('res.currency','currency_rel', 'currency', 'ecommerce_currency', 'Currency'),
        'language_ids': fields.many2many('res.lang', 'lang_rel', 'language','ecommerce_lang', 'Language'),
        'delivery_ids': fields.many2many('delivery.grid', 'delivery_rel', 'delivery', 'ecommrce_delivery', 'Delivery')
        }   
ecommerce_shop()

class ecommerce_category(osv.osv):
       def create(self,cr,uid,vals,context=None):
           
            w_id = vals['web_id']
            if 'category_id' in vals and vals['category_id']:
                cat_id = vals['category_id']
                    
                obj = self.pool.get('product.product').search(cr, uid, [('categ_id','=',cat_id)])
                obj_prd = self.pool.get('product.product').read(cr,uid,obj,[], context={})
                temp=[]
                for i in obj_prd:
                    temp+=[i['id']]
                    
                rec = self.pool.get('ecommerce.shop').write(cr,uid,w_id,{'products':[(6,0,temp)]})
            result = super(osv.osv, self).create(cr, uid, vals, context)
            return result
       
       def write(self,cr,uid,ids,vals,context=None):
            
            obj=self.browse(cr,uid,ids[0])
            curr_id =self.pool.get('ecommerce.shop').browse(cr, uid, ids,context=context)
            web_id = obj.web_id.id
         
            if web_id:
                if 'category_id' in vals and vals['category_id']:
                        cat_id = vals['category_id']
                        obj = self.pool.get('product.product').search(cr, uid, [('categ_id','=',cat_id)])
                        obj_prd = self.pool.get('product.product').read(cr,uid,obj,[], context={})
                        temp=[]
                        for i in obj_prd:
                            temp+=[i['id']]
                        rec = self.pool.get('ecommerce.shop').write(cr,uid,[web_id],{'products':[(6,0,temp)]})
                
            return super(ecommerce_category,self).write(cr,uid,ids,vals,context)
  
       _name = "ecommerce.category"
       _description = "ecommerce category"
       _columns = {
            'name': fields.char('E-commerce Category', size=64, required=True),
            'web_id': fields.many2one('ecommerce.shop', 'Webshop'),
            'category_id': fields.many2one('product.category', 'Tiny Category'),
            'parent_category_id':fields.many2one('ecommerce.category','Parent Category'),
            'child_id': fields.one2many('ecommerce.category', 'parent_category_id', string='Childs Categories'),        
    }
       
ecommerce_category() 
       

