import datetime
import time
import netsvc
from osv import fields,osv
import ir
import pooler
import tools


class products_attribute_name(osv.osv):
    _name = "products.attribute.name"
    _description = "Products Attribute Name"
    _columns = {
        'name': fields.char('Attribute Name', size=256),
        'code': fields.char('Code', size=16),
    }
products_attribute_name()

class products_attribute(osv.osv):
    _name = "products.attribute.value"
    _description = "Products Attribute Value"
    _columns = {
        'name': fields.char('Attribute Value', size=256),
        'attribute_id': fields.many2one('products.attribute.name','Attribute'),
        'product_id': fields.many2one('product.product', 'Product'),
        'price_extra': fields.float('Extra Price', digits=(16,2)),
    }
products_attribute()

class product_product(osv.osv):
    _inherit = "product.product"
    _columns = {
        'attribute_ids': fields.one2many('products.attribute.value','product_id','Attribute'),
        'product_logo': fields.binary('Product Logo'),
        'shop_id': fields.many2one("shop.basic", "Web Shop"),
        
    }
product_product()

class special_products(osv.osv):
    _name="product.special"
    _description="Special Offers"
    _columns={
              'offername':fields.char('Offer Name',size=64,required=True),
              'product': fields.many2one('product.product', 'Product',required=True),
              'list_price':fields.float('List Price', digits=(16,2)),
              'new_price': fields.float('Special Price', digits=(16,2)),
              'expiry_date':fields.date('Expiry Date',required=True),
              'shop_id': fields.many2one("shop.basic", "Web Shop",required=True),
              }
    
    def onchange_product_id(self, cr, uid, ids, product_id):
        result = {}
        if not product_id:
            return {'value':{'list_price': 0.0}}
        add_data = self.pool.get('product.product').browse(cr,uid,product_id)
        result['list_price']=add_data.list_price or 0.0
        return {'value':result}
    
special_products()


class reviews(osv.osv):
    _name="product.reviews"
    _description="Reviews about product"
    _columns={
              'product':fields.many2one('product.product','Product'),
              'customer':fields.many2one('res.partner','Customer'),
              'reviewdate':fields.date('Review Date'),
              'rating':fields.integer('Rating'),
              'review':fields.text('Review')
              }
    
    _defaults = {
        'reviewdate': lambda *a: time.strftime('%Y-%m-%d'),
    }
    
reviews()


