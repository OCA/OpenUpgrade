
from osv import fields, osv

class account_invoice(osv.osv):
	_name = "account.invoice"
	_inherit="account.invoice"
	_columns = {
		'user_id': fields.many2one('res.users', 'Salesman'),
	}
	_defaults = {
		'user_id': lambda self,cr,uid,ctx: uid
	}
account_invoice()
