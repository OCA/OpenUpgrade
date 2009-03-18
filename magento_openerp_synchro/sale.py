from osv import fields,osv

class sale_order(osv.osv):
    _inherit = 'sale.order'
    _columns = {
        'magento_id': fields.integer('Magento order id'),
        'has_error': fields.integer('Magento order error'),
    }
    _defaults = {
        'magento_id': lambda *a: 0,
        'has_error': lambda *a: 0,
    }
    
    def magento_import(self, cr, uid, order_ids, context):
        pass
        
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