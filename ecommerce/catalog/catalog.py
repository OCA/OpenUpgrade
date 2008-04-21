import datetime
import time
import netsvc
from osv import fields,osv
import ir
import pooler
import tools


class product_product(osv.osv):
    _inherit = "product.product"
    _columns = {
                'product_logo': fields.binary('Product Logo'),
                'shop_id': fields.many2many('shop.basic','ecommerce_product_table','ecommerce_products','product','Web shop'),
}
product_product()

class specail_offer(osv.osv):
    _inherit = "product.pricelist.version"
    _columns = {
                'offer_name': fields.char('OfferName',size=64)
        
    }
specail_offer()

class reviews(osv.osv):
    _name="ecommerce.product.reviews"
    _rec_name="product"
    _description="Reviews about product"
    _columns={
              'product':fields.many2one('product.product','Product', required=True, ondelete='cascade'),
              'customer':fields.many2one('res.partner','Customer', required=True, ondelete='cascade'),
              'reviewdate':fields.date('Review Date'),
              'rating':fields.integer('Rating'),
              'review':fields.text('Review')
              }
    
    _defaults = {
        'reviewdate': lambda *a: time.strftime('%Y-%m-%d'),
    }
    
reviews()