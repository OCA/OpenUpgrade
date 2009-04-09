from osv import fields,osv

class product_supplierinfo(osv.osv):
    _inherit = "product.supplierinfo"
    
    _columns = {
        "direct_delivery_flag" : fields.boolean('Direct delivery possible ?'),
    }

product_supplierinfo()


class product_product(osv.osv):
    _inherit = "product.product"

    def _is_direct_delivery_from_product(self, cr, uid, ids, name, arg, context=None):
        res = {}
        def is_direct_delivery_from_suppliers(product):
            cr.execute('select direct_delivery_flag from product_supplierinfo inner join res_partner on product_supplierinfo.name = res_partner.id where product_id=%d and active=true order by sequence ASC LIMIT 1;' % product.id)
            result = cr.fetchone()
            if result and result[0]:
                return True
            return False
        
        for product in self.browse(cr, uid, ids):
            if context.has_key('qty'):
                if product.virtual_available < context['qty']: #TODO deal with partial availability?
                    res[product.id] = is_direct_delivery_from_suppliers(product)
                else: #available in stock
                    res[product.id] = False
            else: #no quantity mentioned so we answer for 'any' quantity
                res[product.id] = is_direct_delivery_from_suppliers(product)
        return res
    
    _columns = {
        'is_direct_delivery_from_product': fields.function(_is_direct_delivery_from_product, method=True, type='boolean', string="Is Supplier Direct Delivery Automatic?"),
    }
    
product_product()
