def purchase_order(osv.osv):
	_inherit = 'purchase.order'
	def wkf_approve_order(self, cr, uid, ids):
		res = super(purchase_order,self).wkf_approve_order(cr, uid, ids)
		for po in self.browse(cr, uid, ids):
			part_id = po.partner_id.id
			cids = self.pool.get('res.company').search(cr, uid, [('partner_id','=',part_id)])
			if cids:
				sale_obj = self.pool.get('sale.order')
				sale_line_obj = self.pool.get('sale.order.line')
				partner_obj = self.pool.get('res.partner')

				shop_id = self.pool.get('sale.shop').search(cr, uid, [])[0]


				new_ids = []

				user = pool.get('res.users').browse(cr, uid, uid)
				partner_id = user.company_id.partner_id.id
				partner_addr = partner_obj.address_get(cr, uid, [partner_id],
						['invoice', 'delivery', 'contact'])
				default_pricelist = partner_obj.browse(cr, uid, partner_id,
							context).property_product_pricelist.id

				vals = {
					'origin': 'PO:%s' % str(po.name),
					'picking_policy': 'direct',
					'shop_id': shop_id,
					'partner_id': partner_id,
					'pricelist_id': default_pricelist,
					'partner_invoice_id': partner_addr['invoice'],
					'partner_order_id': partner_addr['contact'],
					'partner_shipping_id': partner_addr['delivery'],
					'order_policy': 'manual',
					'date_order': now(),
					'order_policy': po.invoice_method=='picking' and 'picking' or 'manual'
				}
				new_id = sale_obj.create(cr, uid, vals)

				for line in po.order_line:
					value = sale_line_obj.product_id_change(cr, uid, [], default_pricelist,
							line.product_id.id, qty=line.product_qty, partner_id=partner_id)['value']
					value['price_unit'] = line.price_unit
					value['product_id'] = line.product_id.id
					value['product_uos'] = value.get('product_uos', [False,False])[0]
					value['product_uom_qty'] = line.product_qty
					value['order_id'] = new_id
					sale_line_obj.create(cr, uid, value)

		return res

