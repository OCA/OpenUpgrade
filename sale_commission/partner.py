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
		'agent': fields.many2one('sale.agent','Salesagent'),
	}
res_partner()

#
# En Sale_agent class
#
