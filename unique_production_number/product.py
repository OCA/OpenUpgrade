from osv import fields, osv
import tools
import ir
import pooler


class product_product(osv.osv):
    _inherit = "product.product"
    
    _columns = {
        'unique_production_number': fields.boolean('Unique Production Number'),
    }
    
product_product()