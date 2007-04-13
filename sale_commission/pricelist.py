import math
from osv import fields,osv
import tools
import ir
import pooler

class product_pricelist(osv.osv):
	_name = "product.pricelist"
        _description = "sale agent commission Rate"
        _inherit="product.pricelist"
	_columns = {
		'commrate':fields.integer('Commission Rate(%)'),
                }
product_pricelist()

