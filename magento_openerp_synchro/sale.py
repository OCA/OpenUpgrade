from osv import fields,osv

class sale_order(osv.osv):
    _inherit = 'sale.order'
    _columns = {
        'magento_id': fields.integer('magento order id'),
        'has_error': fields.integer('magento order error'),
    }
    _defaults = {
        'magento_id': lambda *a: 0,
        'has_error': lambda *a: 0,
    }
sale_order()


class sale_shop(osv.osv):
    _inherit = 'sale.shop'
    _columns = {
        'magento_flag': fields.boolean('Magento webshop'),
    }
    _defaults = {
        'magento_flag': lambda *a: False,
    }  
sale_shop()