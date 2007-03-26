import math
from osv import fields,osv
import tools
import ir
import pooler

class sale_agent(osv.osv):
	_name = "sale.agent"
        _description = "Sale agent sale info"
	_columns = {
               
               'name': fields.char('Saleagent Name', size=25, required=True),
               'partner_id': fields.many2one('res.partner','Partner',size=64, required=True,ondelete='cascade'),
               'comprice_id': fields.many2one('product.pricelist','commission price list', size=25, required=True,ondelete='cascade'),                
	       'active': fields.boolean('Active'),                               
	}
	_defaults = {
               
                }
sale_agent()

#
# En Sale_agent class
#
