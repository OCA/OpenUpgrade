from osv import fields,osv
from osv import orm


#class hr_timesheet_sheet(osv.osv):
#	_inherit="hr.timesheet.sheet"
#	_columns={
#		"to_invoice": ???
#		}
#hr_timesheet_sheet()


#class account_analytic_account(osv.osv):
#	_inherit = "account.analytic.account"
#	_columns = {
#		'to_invoice': fields.many2one('hr_timesheet_invoice.factor','Default Invoicing'),
#		'journal_invoicing': fields.many2many('obj', 'table_name', 'id1', 'id2', "string"),
#
#	}
#account_analytic_account()


class user_product_ca(osv.osv):

	_name="user_product_ca"
	_description= "Relation table between users, products and analytic account"
	_columns={
		'user_id': fields.many2one("res.users","User",required=True,),
		'product_id': fields.many2one("product.product","Product",),
		'account_id': fields.many2one("account.analytic.account", "Analytic Account",),
		'rate_id': fields.many2one("hr_timesheet_invoice.factor", "Invoicing Rate",),
		}

user_product_ca()


class account_analytic_account(osv.osv):

	_inherit = "account.analytic.account"
	_columns = {
		'user_product' : fields.one2many('user_product_ca', 'account_id', 'Users/Products Rel.'),
	}

account_analytic_account()


class hr_analytic_timesheet(osv.osv):

	_inherit = "hr.analytic.timesheet"

	def on_change_account_id(self, cr, uid, ids,user_id, account_id):
		res = {}
		if not (account_id):
			return res 
		if not (user_id):
			return super(hr_analytic_timesheet, self).on_change_account_id(cr, uid, ids,account_id)

		res.setdefault('value',{})
		temp = self.pool.get('user_product_ca').search(cr, uid, [('user_id', '=', user_id),('account_id', '=', account_id) ])

		if not temp:
			return super(hr_analytic_timesheet, self).on_change_account_id(cr, uid, ids,account_id)
		else:
			r = self.pool.get('user_product_ca').browse(cr, uid, temp)[0]
			if r.rate_id.id:
				res['value']['to_invoice']= r.rate_id.id
			else: 
				res['value']['to_invoice']= super(hr_analytic_timesheet, self).on_change_account_id(cr, uid, ids,account_id)['value']['to_invoice']
			if r.product_id.id:
				res['value']['product_id'] = r.product_id.id
	
		return res

	def on_change_user_id(self, cr, uid, ids,user_id, account_id):

		res = {}
		if not (user_id):
			return res 
		res = super(hr_analytic_timesheet, self).on_change_user_id(cr, uid, ids,user_id)

		if account_id:
			temp = self.pool.get('user_product_ca').search(cr, uid, [('user_id', '=', user_id),('account_id', '=', account_id) ])
			if temp:
				r = self.pool.get('user_product_ca').browse(cr, uid, temp)[0]
				if r.rate_id.id:
					res['value']['to_invoice']= r.rate_id.id 
				if r.product_id.id:
					res['value']['product_id'] = r.product_id.id	
	
		return res

hr_analytic_timesheet()

