from osv import fields,osv


#class account_invoice_abstract_line_type(osv.osv):
#	_name = "account.invoice.abstract.line.type"
#	_description = "Invoice Abstract Line Type"
#	_columns = {
#		'name': fields.char('Name', size=64, required=True),
#		'code': fields.char('Code', size=64, required=True),
#		'field_ids': fields.one2many('account.invoice.abstract.line.type.field', 'abstract_inv_line_type_id', 'Type Fields'),
#	}
#account_invoice_abstract_line_type()
#
#
#class account_invoice_abstract_line_type_field(osv.osv):
#	_description='Account Invoice Abstract Line Type Fields'
#	_name = 'account.invoice.abstract.line.type.field'
#	_columns = {
#		'name': fields.char('Field Name', size=64, required=True),
#		'abstract_inv_line_type_id': fields.many2one('account.invoice.abstract.line.type', 'Invoice Abstract Line Type', required=True, ondelete='cascade'),
#		'required': fields.boolean('Required'),
#		'readonly': fields.boolean('Readonly'),
#		'size': fields.integer('Max. Size'),
#		'visible': fields.boolean('Visible'),
#	}
#account_invoice_abstract_line_type_field()


class account_invoice_line(osv.osv):
#	def _inv_line_type_get(self, cr, uid, context=None):
#		inv_line_type_obj = self.pool.get('account.invoice.abstract.line.type')
#
#		result = []
#		type_ids = inv_line_type_obj.search(cr, uid, [])
#		inv_line_types = inv_line_type_obj.browse(cr, uid, type_ids)
#		for inv_line_type in inv_line_types:
#			result.append((inv_line_type.code, inv_line_type.name))
#		return result

	def fields_get(self, cr, uid, fields=None, context=None):
		states = {
			'product_id': {
				'article': [('readonly', False)],
				'text': [('readonly', True)],
				'subtotal': [('readonly', True)],
				'title': [('readonly', True)],
				'break': [('readonly', True)],
				'line': [('readonly', True)],
				},
			'account_id': {
				'article': [('readonly', False)],
				'text': [('readonly', True)],
				'subtotal': [('readonly', True)],
				'title': [('readonly', True)],
				'break': [('readonly', True)],
				'line': [('readonly', True)],
				},
		}
		res = super(account_invoice_line, self).fields_get(cr, uid, fields, context)
		for field in res:
			if states.has_key(field):
				for key,value in states[field].items():
					res[field].setdefault('states',{})
					res[field]['states'][key] = value
		return res

#		inv_line_type_obj = self.pool.get('account.invoice.abstract.line.type')
#		type_ids = inv_line_type_obj.search(cr, uid, [])
#		types = inv_line_type_obj.browse(cr, uid, type_ids)
#		for type in types:
#			for field in self.pool.get('account.invoice.line.field'):
#				if field.name in res:
#					res[field.name].setdefault('states', {})
#					res[field.name]['states'][type.code] = [
#							('readonly', field.readonly),
#							('required', field.required)]
#		return res

	_name = "account.invoice.line"
	_description = "Invoice Line"
	_inherit = "account.invoice.line"
	_columns = {
		'state': fields.selection([
				('article','Article'),
				('text','Text'),
				('subtotal','Sub Total'),
				('title','Title'),
				('break','Page Break'),
				('line','Line'),]
			,'Type', select=True),

#		'state': fields.selection(_inv_line_type_get, 'Type', required=True, change_default=True),

		'sequence': fields.integer('Sequence Number'),
#		'account_id': fields.many2one('account.account', 'Source Account', required=False, domain=[('type','<>','view'), ('type', '<>', 'closed')]),
	}

	def _default_account(self, cr, uid, context=None):
		#[('code','=','0')]
		cr.execute("select id from account_account where code = 0 LIMIT 1")
		res=cr.fetchone()
		return res[0]


	_defaults = {
		'state': lambda *a: 'article',
		'account_id': _default_account
	}
account_invoice_line()


#class account_invoice_layout_line(osv.osv):
#	_name = "account.invoice.layout.line"
#	_description = "Invoice Layout Line"
#	_inherit = "account.invoice.line"
#	_columns = {
#		'account_id': fields.many2one('account.account', 'Source Account', required=False, domain=[('type','<>','view'), ('type', '<>', 'closed')]),
#	}
#account_invoice_layout_line()

#class account_invoice_line_abstract(osv.osv):

#	def init(self, cr):
#		cr.execute("""
#			create or replace view account_invoice_line_abstract as 
#			((select id,name,invoice_id,uos_id,product_id,account_id,price_unit,
#				quantity,discount,note,account_analytic_id,'article' as state,sequence 
#				from account_invoice_line) 
#			union 
#			(select -id,name,invoice_id,uos_id,product_id,account_id,price_unit,
#				quantity,discount,note,account_analytic_id,state,sequence 
#				from account_invoice_layout_line))
#		""")

#	def write(self, cr, user, ids, vals, context=None):
#		for id in ids:
#			if id > 0:
#				self.pool.get('account.invoice.line').write(cr, user, id, vals, context)
#			else:
#				self.pool.get('account.invoice.layout.line').write(cr, user, -id, vals, context)		
#		return True

#	def read(self, cr, user, ids, fields=None, context=None, load='_classic_read'):
#		tmp = []
#		for id in ids:
#			if id > 0:
#				tmp.append(self.pool.get('account.invoice.line').read(cr, user, id, fields, context, load))
#			else:
#				res = self.pool.get('account.invoice.layout.line').read(cr, user, -id, fields, context, load)
#				res['id'] = -res['id']
#				tmp.append(res)
#		return tmp

#	def create(self, cr, user, vals, context=None):
#		if vals.get('state', 'article') == 'article':
#			vals['state'] = 'article'
#			return self.pool.get('account.invoice.line').create(cr, user, vals, context)
#		return -self.pool.get('account.invoice.layout.line').create(cr, user, vals, context)

#	def unlink(self, cr, uid, ids, context=None):
#		for id in ids:
#			if id > 0:
#				self.pool.get('account.invoice.line').unlink(cr, uid, id, context)
#			else:
#				self.pool.get('account.invoice.layout.line').unlink(cr, uid, -id, context)
#		return True

#	_name = "account.invoice.line.abstract"
#	_description = "Invoice Abstract Line"
#	_auto = False
#	_order = 'sequence'
#	_inherit = "account.invoice.layout.line"
#	_columns = {
##		'name': fields.char('Description', size=256, required=True),
##		'invoice_id': fields.many2one('account.invoice', 'Invoice Ref', ondelete='cascade', select=True),
##		'uos_id': fields.many2one('product.uom', 'Unit', ondelete='set null'),
##		'product_id': fields.many2one('product.product', 'Product', ondelete='set null'),
##		'account_id': fields.many2one('account.account', 'Source Account', domain=[('type','<>','view'), ('type', '<>', 'closed')]),
##		'price_unit': fields.float('Unit Price',),
##		'price_subtotal': fields.float(string='Subtotal'),
##		'quantity': fields.float('Quantity'),
##		'discount': fields.float('Discount (%)', digits=(16,2)),
##		'invoice_line_tax_id': fields.many2many('account.tax', 'account_invoice_line_tax', 'invoice_line_id', 'tax_id', 'Taxes', domain=[('parent_id','=',False)]),
##		'note': fields.text('Notes'),
##		'account_analytic_id':  fields.many2one('account.analytic.account', 'Analytic Account'),
#	}

#account_invoice_line_abstract()

class one2many_mod2(fields.one2many):
	def get(self, cr, obj, ids, name, user=None, offset=0, context=None, values=None):
		if not context:
			context = {}
		if not values:
			values = {}
		res = {}
		for id in ids:
			res[id] = []
		ids2 = obj.pool.get(self._obj).search(cr, user, [(self._fields_id,'in',ids),('state','=','article')], limit=self._limit)
		for r in obj.pool.get(self._obj)._read_flat(cr, user, ids2, [self._fields_id], context=context, load='_classic_write'):
			res[r[self._fields_id]].append( r['id'] )
		return res


#class account_invoice(osv.osv):
#	_inherit = "account.invoice"
#	_columns = {
#		'abstract_line_ids': fields.one2many('account.invoice.line', 'invoice_id', 'Invoice Lines', states={'draft':[('readonly',False)]}),
#		'line_ids': one2many_mod2('account.invoice.line', 'invoice_id', 'Invoice Lines', states={'draft':[('readonly',False)]}),
#	}
#account_invoice()
