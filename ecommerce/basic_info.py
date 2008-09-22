# -*- encoding: utf-8 -*-
from osv import fields , osv                                                       
import datetime
import time
import netsvc
import ir


class ecommerce_payment(osv.osv):
    _name = "ecommerce.payment"
    _description = "ecommerce Payment"
    _columns = {
        'name': fields.char('Cheque Payable to', size=256, required=True),
        'street': fields.char('Street', size=128, required=True),
        'street2': fields.char('Street2', size=128, required=True),
        'zip': fields.char('Zip', change_default=True, size=24, required=True),
        'city': fields.char('City', size=128, required=True),
        'state_id': fields.many2one("res.country.state", 'State', required=True),
        'country_id': fields.many2one('res.country', 'Country', required=True),
    }
ecommerce_payment()


class ecommerce_shop(osv.osv):
    _name = "ecommerce.shop"
    _description = "Shop Basic Info"
    _columns = {
        'name': fields.char('Name', size=256),
        'company_id': fields.many2one('res.company', 'Company'),
        'shop_id': fields.many2one('sale.shop', 'Sale Shop'),
        'chequepay_to':fields.many2one('ecommerce.payment', 'Cheque Payable to'),
        'category_ids': fields.one2many('ecommerce.category', 'web_id','Categories', translate=True),
        'products':fields.many2many('product.product','ecommerce_new_product_rel','product','ecommerce_product','Products',readonly=True),
        'currency_id': fields.many2many('res.currency','currency_rel', 'currency', 'ecommerce_currency', 'Currency'),
        'language': fields.many2many('res.lang', 'lang_rel', 'language','ecommerce_lang', 'Language'),
        'delivery': fields.many2many('delivery.grid', 'delivery_rel', 'delivery', 'ecommrce_delivery', 'Delivery')
        
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
       

