import math
from osv import fields,osv
import tools
import ir
import pooler

class sale_agent(osv.osv):
	_name = "sale.agent"
	_description = "Sale agent"
	_columns = {
		'name': fields.char('Saleagent Name', size=25, required=True),
		'partner_id': fields.many2one('res.partner','Sale agent address',required=True,ondelete='cascade'),
		'customer_ids':fields.one2many('res.partner','agent_id','Customers'),
		'comprice_id': fields.many2one('product.pricelist','Commission price list',required=True),
		'active': fields.boolean('Active'),
	}
	_defaults = {
		'active': lambda *a: True,
	}
sale_agent()

