from osv import osv, fields


class Product(osv.osv):
	_inherit = 'product.product'

	def _partner_ref2(self, cursor, user, ids, name, arg, context=None):
		res = {}
		for product in self.browse(cursor, user, ids, context=context):
			res[product.id] = '\n'.join([x.product_code \
					for x in product.seller_ids if x.product_code]) or ''
		return res

	def _partner_ref2_search(self, cursor, user, obj, name, args):
		supplierinfo_obj = self.pool.get('product.supplierinfo')
		args = args[:]
		i = 0
		while i < len(args):
			args[i] = ('product_code', args[i][1], args[i][2])
			i += 1
		supplierinfo_ids = supplierinfo_obj.search(cursor, user, args)
		product_ids = [ x.product_id.id for x in supplierinfo_obj.browse(cursor, user,
				supplierinfo_ids) if x.product_id]
		return [('id', 'in', product_ids)]

	_columns = {
		'partner_ref2': fields.function(_partner_ref2, method=True,
			type='char', string='Customer ref', fnct_search=_partner_ref2_search,
			select=2),
	}

	def name_search(self, cursor, user, name='', args=None, operator='ilike',
			context=None, limit=80):
		ids = self.search(cursor, user, [('partner_ref2', '=', name)] + args,
				limit=limit, context=context)
		if ids:
			return self.name_get(cursor, user, ids, context=context)
		return super(Product, self).name_search(cursor, user, name=name, args=args,
				operator=operator, context=context, limit=limit)

Product()
