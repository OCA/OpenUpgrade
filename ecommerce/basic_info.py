from osv import fields , osv                                                       
import datetime
import time
import netsvc
import ir
from ecommerce import smtp_server
from smtp_server import smtp_connect 

class image_display_config(osv.osv):
    _name = 'image.display.config'
    _description = 'Image Size'
    _columns = {
                'name': fields.char('Name',size=128,required=True),
                'height': fields.float('Width',digits=(16,2)),
                'width': fields.float('Height',digits=(16,2)),
                'scale': fields.selection([('px','Pixel'),('in','Inch')],'Scale'),
    }
image_display_config()


class shop_basic(osv.osv):
    
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
    
    _name = "shop.basic"
    _description = "Shop Basic Info"
    _columns = {
        'name': fields.char('Name', size=256),
        'company_id': fields.many2one('res.company', 'Company'),
        'partner_id': fields.many2one('res.company', 'Owner'),
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
        'category_ids': fields.one2many('ecommerce.category', 'webid','Categories'),
        'products':fields.many2many('product.product','ecommerce_new_product_rel','product','ecommerce_product','Products'),
     
    }
shop_basic()

class ecommerce_category(osv.osv):
    
    def create(self,cr,uid,vals,context={}):
        ecom_id = super(ecommerce_category,self).create(cr,uid,vals,context)
        self.write(cr,uid,ecom_id,{'ecommerce_id':ecom_id})
        return ecom_id

    _name = "ecommerce.category"
    _description = "ecommerce category"
    _columns = {
        'name': fields.char('Name', size=64, required=True),
        'ecommerce_id': fields.integer('Web ID', readonly=True),
        'webid': fields.many2one('shop.basic', 'Website'),
        'category_id': fields.many2one('product.category', 'Category'),
        'include_childs': fields.boolean('Include Childs'),
    }
ecommerce_category()

class product_category(osv.osv):
    _inherit = "product.category"
    _columns = {
        'category_image': fields.binary('Category Image'),
        'shop_id': fields.many2one("shop.basic", "Web Shop"),
    }

    def write(self, cr, user, ids, values, context={}):
        product_pool = self.pool.get('product.product')
        categ = self.read(cr,user,ids,['shop_id'])[0]

        product_ids = product_pool.search(cr,user,[('categ_id','=',ids[0])])
        if categ['shop_id']:
            product_pool.write(cr,user,product_ids,{'shop_id':categ['shop_id'][0]})
        return super(product_category,self).write(cr, user, ids, values, context)

product_category()