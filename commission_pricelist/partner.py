import math
from osv import fields,osv
import tools
import ir
import pooler

class res_partner(osv.osv):
	_name = "res.partner"
        _description = "Sale agent sale info"
        _inherit="res.partner"
	_columns = {
                #'agent_id': fields.one2many('sale.agent','partner_id','salesagent', required=True),
                  'agent_id': fields.many2one('sale.agent','saleagent'),
                }
res_partner()

