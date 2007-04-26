import math
from osv import fields,osv
import tools
import ir
import pooler

class res_partner(osv.osv):
	_inherit="res.partner"
	_columns = {
		'agent_id': fields.many2one('sale.agent','Saleagent'),
	}
res_partner()

