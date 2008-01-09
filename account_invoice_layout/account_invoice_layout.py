from osv import fields,osv


class account_invoice_line(osv.osv):

	def fields_get(self, cr, uid, fields=None, context=None):
		article = {
			'article': [('readonly', False), ('invisible', False)],
			'text': [('readonly', True), ('invisible', True), ('required', False)],
			'subtotal': [('readonly', True), ('invisible', True), ('required', False)],
			'title': [('readonly', True), ('invisible', True)],
			'break': [('readonly', True), ('invisible', True)],
			'line': [('readonly', True), ('invisible', True)],
		}
		states = {
			'name': {
				'break': [('readonly', True),('required', True)],
				'line': [('readonly', True),('required', True)],
				},
			'product_id': article,
			'account_id': article,
			'quantity': article,
			'uos_id': article,
			'price_unit': article,
			'discount': article,
			'invoice_line_tax_id': article,
			'account_analytic_id': article,
		}
		res = super(account_invoice_line, self).fields_get(cr, uid, fields, context)
		for field in res:
			if states.has_key(field):
				for key,value in states[field].items():
					res[field].setdefault('states',{})
					res[field]['states'][key] = value
		return res

	def _onchange_invoice_line_view(self, cr, uid, id, type, context={}, *args):

		if (not type):
			return {}
		if type != 'article':
			temp = {'value': {
					'product_id': False, 
					'uos_id': False,
					'account_id': False,
					'price_unit': False,
					'price_subtotal': False,
					'quantity': 0,
					'discount': False,
					'invoice_line_tax_id': False,
					'account_analytic_id': False,
					},
				}
			if type == 'line':
				temp['value']['name'] = '-----------------------------------------'
			if type == 'break':
				temp['value']['name'] = 'PAGE BREAK'
			if type == 'subtotal':
				temp['value']['name'] = 'Sub Total'
			return temp
		return {}

	def create(self, cr, user, vals, context=None):
		if vals.has_key('state'):
			if vals['state'] == 'line':
				vals['name'] = '-----------------------------------------'
			if vals['state'] == 'break':
				vals['name'] = 'PAGE BREAK'
			if vals['state'] != 'article':
				vals['quantity']= 0
		return super(account_invoice_line, self).create(cr, user, vals, context)

	def write(self, cr, user, ids, vals, context=None):
		if vals.has_key('state'):
			if vals['state'] != 'article':
				vals['product_id']= False
				vals['uos_id']= False
				vals['account_id']= self._default_account(cr, user, None)
				vals['price_unit']= False
				vals['price_subtotal']= False
				vals['quantity']= 0
				vals['discount']= False
				vals['invoice_line_tax_id']= False
				vals['account_analytic_id']= False
			if vals['state'] == 'line':
				vals['name'] = '-----------------------------------------'
			if vals['state'] == 'break':
				vals['name'] = 'PAGE BREAK'
			if vals['state'] == 'subtotal':
				vals['name'] = 'Sub Total'
		return super(account_invoice_line, self).write(cr, user, ids, vals, context)

	_name = "account.invoice.line"
	_order = "invoice_id, sequence asc"
	_description = "Invoice Line"
	_inherit = "account.invoice.line"
	_columns = {
		'state': fields.selection([
				('article','Product'),
				('text','Text'),
				('subtotal','Sub Total'),
				('title','Title'),
				('break','Page Break'),
				('line','Line'),]
			,'Type', select=True),
		'sequence': fields.integer('Sequence Number'),
	}
	def _default_account(self, cr, uid, context=None):
		cr.execute("select id from account_account where code = 0 LIMIT 1")
		res=cr.fetchone()
		return res[0]
	_defaults = {
		'state': lambda *a: 'article',
		'account_id': _default_account
	}
account_invoice_line()


class one2many_mod2(fields.one2many):
	def get(self, cr, obj, ids, name, user=None, offset=0, context=None, values=None):
		if not context:
			context = {}
		if not values:
			values = {}
		res = {}
		for id in ids:
			res[id] = []
		print self.fields
		ids2 = obj.pool.get(self._obj).search(cr, user, [(self._fields_id,'in',ids),('state','=','article')], limit=self._limit)
		for r in obj.pool.get(self._obj)._read_flat(cr, user, ids2, [self._fields_id], context=context, load='_classic_write'):
			res[r[self._fields_id]].append( r['id'] )
		return res


class account_invoice(osv.osv):
	_inherit = "account.invoice"
	_columns = {
		'abstract_line_ids': fields.one2many('account.invoice.line', 'invoice_id', 'Invoice Lines', states={'draft':[('readonly',False)]}),
		'line_ids': one2many_mod2('account.invoice.line', 'invoice_id', 'Invoice Lines', states={'draft':[('readonly',False)]}),
	}
account_invoice()
