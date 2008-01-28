from osv import fields,osv
from osv import orm


class analytic_user_funct_grid(osv.osv):

	_name="analytic_user_funct_grid"
	_description= "Relation table between users and products on a analytic account"
	_columns={
		'user_id': fields.many2one("res.users","User",required=True,),
		'product_id': fields.many2one("product.product","Product",required=True,),
		'account_id': fields.many2one("account.analytic.account", "Analytic Account",required=True,),
		}

analytic_user_funct_grid()


class account_analytic_account(osv.osv):

	_inherit = "account.analytic.account"
	_columns = {
		'user_product_ids' : fields.one2many('analytic_user_funct_grid', 'account_id', 'Users/Products Rel.'),
	}

account_analytic_account()


class hr_analytic_timesheet(osv.osv):

	_inherit = "hr.analytic.timesheet"


	def on_change_account_id(self, cr, uid, ids,user_id, account_id):
		res = {}
		if not (account_id):
			#avoid a useless call to super
			return res 

		if not (user_id):
			return super(hr_analytic_timesheet, self).on_change_account_id(cr, uid, ids,account_id)

		#get the browse record related to user_id and account_id
		temp = self.pool.get('analytic_user_funct_grid').search(cr, uid, [('user_id', '=', user_id),('account_id', '=', account_id) ])

		if not temp:
			#if there isn't any record for this user_id and account_id
			return super(hr_analytic_timesheet, self).on_change_account_id(cr, uid, ids,account_id)
		else:
			#get the old values from super and add the value from the new relation analytic_user_funct_grid
			r = self.pool.get('analytic_user_funct_grid').browse(cr, uid, temp)[0]
			res.setdefault('value',{})
			res['value']= super(hr_analytic_timesheet, self).on_change_account_id(cr, uid, ids,account_id)['value']
			res['value']['product_id'] = r.product_id.id
	
		return res


	def on_change_user_id(self, cr, uid, ids,user_id, account_id):
		res = {}
		if not (user_id):
			#avoid a useless call to super
			return res 

		#get the old values from super
		res = super(hr_analytic_timesheet, self).on_change_user_id(cr, uid, ids,user_id)

		if account_id:
			#get the browse record related to user_id and account_id
			temp = self.pool.get('analytic_user_funct_grid').search(cr, uid, [('user_id', '=', user_id),('account_id', '=', account_id) ])
			if temp:
				#add the value from the new relation analytic_user_funct_grid
				r = self.pool.get('analytic_user_funct_grid').browse(cr, uid, temp)[0]
				res['value']['product_id'] = r.product_id.id	
	
		return res

hr_analytic_timesheet()

