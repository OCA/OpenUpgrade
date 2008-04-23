from osv import fields , osv                                                       
import datetime
import time
import netsvc
import ir

class ecommerce_shop(osv.osv):
    
    def _email_send(self, cr, uid, ids, email_from, subject, body, on_error=None):
        partners = self.browse(cr, uid, ids)
        for partner in partners:
            if len(partner.address):
                if partner.address[0].email:
                    tools.email_send(email_from, [partner.address[0].email], subject, body, on_error)
        return True

    def email_send(self, cr, uid, ids, email_from, subject, body, on_error=''):
        while len(ids):
            self.pool.get('ir.cron').create(cr, uid, {
                'name': 'Send Partner Emails',
                'user_id': uid,
                'model': 'res.partner',
                'function': '_email_send',
                'args': repr([ids[:16], email_from, subject, body, on_error])
            })
            ids = ids[16:]
        return True
    
    _name = "ecommerce.shop"
    _description = "Shop Basic Info"
    _columns = {
        'name': fields.char('Name', size=256),
        'company_id': fields.many2one('res.company', 'Company'),
        'shop_id': fields.many2one('sale.shop', 'Sale Shop', required=True),     
        'display_search_keyword':fields.boolean('Display  Quick Search'),
        'display_category_cnt': fields.boolean('Display Category Count'),
        'price_with_tax': fields.boolean('Price with Tax'),
        'tell_to_friend': fields.boolean('Tell To Friend'),
        'display_cart': fields.boolean('Display Cart After Shopping'),
        'display_product_name_new': fields.boolean('Display Product Name'),
        'display_manufacturer_name_new': fields.boolean('Display Manufacturer Name'),
        'display_product_image': fields.boolean('Display Product Image'),
        'display_product_price': fields.boolean('Display Product Price'),
        'display_product_quantity': fields.boolean('Display Product Quantity'),
        'display_product_weight': fields.boolean('Display Product Weight'),
        'display_partner_logo':fields.boolean('Display Partner Logo'),
        'display_category_context':fields.boolean('Require Category Context'),
        'display_page_offset':fields.boolean('Require Page Offset'),
        'category_ids': fields.one2many('ecommerce.category', 'web_id','Categories'),
        'products':fields.many2many('product.product','ecommerce_new_product_rel','product','ecommerce_product','Products'),
     
    }   
ecommerce_shop()

class ecommerce_category(osv.osv):
    def create(self,cr,uid,vals,context=None):
        ecom_id = super(ecommerce_category,self).create(cr,uid,vals)
        if vals:
            cat_id = self.pool.get('product.category').create(cr,uid,{'name':vals['name']})
            self.pool.get('product.category').write(cr,uid,cat_id,{'ecommerce_cat_id':ecom_id})
            vals.update({'tiny_cat_id':cat_id})
            print "iddd",cat_id
        return ecom_id
#    
    def write(self,cr,uid,ids,vals,context=None):
        print "::::::::::::::",ids,vals,context
        
        if vals['name']:
            cat_id = self.pool.get('product.category').search(cr,uid,[('ecommerce_cat_id','in',ids)])
            self.pool.get('product.category').write(cr,uid,cat_id,{'name':vals['name']})
            
        return super(ecommerce_category,self).write(cr,uid,ids,vals,context)        
    
    _name = "ecommerce.category"
    _description = "ecommerce category"
    _columns = {
        'name': fields.char('E-commerce Category', size=64, required=True),
        'web_id': fields.many2one('ecommerce.shop', 'Webshop'),
        'category_id': fields.many2one('product.category', 'Tiny Category'),
        'include_childs': fields.boolean('Include Childs'),
        'parent_category_id':fields.many2one('ecommerce.category','Parent Category'),
        'child_id': fields.one2many('ecommerce.category', 'parent_category_id', string='Childs Categories'),        
    }
ecommerce_category()

class product_category(osv.osv):
    _inherit = "product.category"
    _columns = {
        'category_image': fields.binary('Category Image'),
        'ecommerce_cat_id':fields.char('Ecommerce id',size=64)
    }

product_category()