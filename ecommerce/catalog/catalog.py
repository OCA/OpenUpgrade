# -*- encoding: utf-8 -*-
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
                'shop_ids': fields.many2many('ecommerce.shop','ecommerce_new_product_rel','ecommerce_product','product','Web shop'),
}
product_product()

class specail_offer(osv.osv):
    _inherit = "product.pricelist.version"
    _columns = {
                'offer_name': fields.char('OfferName',size=64,translate=True)
	}

specail_offer()

class reviews(osv.osv):
    _name="ecommerce.product.reviews"
    _rec_name="product"
    _description="Reviews about product"
    _columns={
              'product_id':fields.many2one('product.product','Product', required=True, ondelete='cascade'),
              'customer_id':fields.many2one('ecommerce.partner','Customer', required=True, ondelete='cascade'),
              'reviewdate':fields.date('Review Date'),
              'rating':fields.integer('Rating'),
              'review':fields.text('Review')
              }
    
    _defaults = {
        'reviewdate': lambda *a: time.strftime('%Y-%m-%d'),
    }
    
reviews()

