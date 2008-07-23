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
                'currency_id': fields.many2one('res.currency', 'Currency')
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

class shipping_method(osv.osv):
    _name = "ecommerce.shipping.method"
    _description = "Ecommerce Shipping Method"
    _columns = {
                'state_id': fields.many2one("res.country.state", 'State', domain="[('country_id','=',country_id)]"),
                'country_id': fields.many2one('res.country', 'Country', required=True),
                'shipping':fields.one2many('ecommerce.shipping.service','shipp_method','Shipping')
                }
shipping_method()

class shipping_service(osv.osv):
    _name = "ecommerce.shipping.service"
    _rec_name = 'shipping_type'
    _description = "Ecommerce Shipping Service"
    _columns ={
               'shipping_type':fields.selection([('byair','ByAir'), ('ground','Ground'), ('free shipping','Free Shipping'), ('flat rate','Flat Rate'),('home delivery','Home Delivery')], 'Shipping Type', required=True),
               'shipping_charge':fields.float('Charges',required=True),
               'currency':fields.many2one('res.currency','Currency',required=True),
               'country_id': fields.many2one('res.country', 'Country', required=True),
               'shipp_method':fields.many2one('ecommerce.shipping.method','Shipping Method')
               }
shipping_service()
