##############################################################################
#
# Copyright (c) 2004-2006 TINY SPRL. (http://tiny.be) All Rights Reserved.
#
#
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsability of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# garantees and support are strongly adviced to contract a Free Software
# Service Company
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
##############################################################################

import time
import netsvc
from osv import fields, osv
# import ir
from mx import DateTime



class pos_order(osv.osv):
	_name = "pos.order"
	_description = "Point of Sale"

	wf_service = netsvc.LocalService("workflow")

	def _amount_total(self, cr, uid, ids, field_name, arg, context):
		id_set = ",".join(map(str, ids))
		cr.execute("SELECT p.id,COALESCE(SUM(l.price_unit*l.qty*(100-l.discount))/100.0,0)::decimal(16,2) AS amount FROM pos_order p LEFT OUTER JOIN pos_order_line l ON (p.id=l.order_id) WHERE p.id IN ("+id_set+") GROUP BY p.id ")
		res = dict(cr.fetchall())
		return res

	def _amount_tax(self, cr, uid, ids, field_name, arg, context):
		res = {}
		tax_obj = self.pool.get('account.tax')
		for order in self.browse(cr, uid, ids):
			val= 0.0
			for line in order.order_line :
				val = reduce( lambda x, y: x+y['amount'],
						tax_obj.compute_inv(cr, uid, line.product_id.taxes_id,
											line.price_unit * (1-(line.discount or 0.0)/100.0), line.qty),
						val)
			res[order.id]=round(val,2)
		return res

	def _left_to_pay(self, cr, uid, ids, field_name, arg, context):
		res = {}
		tot= self._amount_total(cr, uid, ids, field_name, arg, context)
		for order in self.browse(cr, uid, ids):
			val = 0.0
			for payment in order.payment_ids:
				val+= payment.amount
			res[order.id]=  tot[order.id] - val
		return res

	def _payment_return(self, cr, uid, ids, field_name, arg, context):
		res={}
		tots = self._amount_total(cr, uid, ids, field_name, arg, context)
		for order in  self.browse(cr, uid, ids):
			res[order.id]= order.payment_amount - tots[order.id]
		return res

	def _journal_get(self, cr, uid, context={}):
		obj = self.pool.get('account.journal')
		ids = obj.search(cr, uid, [('type','=','cash')])
		res = obj.read(cr, uid, ids, ['id', 'name'], context)
		res = [(r['id'], r['name']) for r in res]
		return res


	_columns = {

		'name': fields.char('Order Description', size=64, required=True, states={'draft':[('readonly',True)]}),
		'shop_id':fields.many2one('sale.shop', 'Shop', required=True, states={'draft':[('readonly',False)]}, readonly=True),
		'date_order':fields.date('Date Ordered', required=True, readonly=True,),
		'date_validity':fields.date('Validity Date', required=True, readonly=True),
		'user_id':fields.many2one('res.users', 'Salesman',  relate=True, readonly=True),
# 		'amount_untaxed': fields.function(_amount_untaxed, method=True, string='Untaxed Amount'),
 		'amount_tax': fields.function(_amount_tax, method=True, string='Taxes'),
 		'amount_total': fields.function(_amount_total, method=True, string='Total'),
 		'order_line': fields.one2many('pos.order.line', 'order_id', 'Order Lines', states={'draft':[('readonly',False)]}, readonly=True ),
 		'payment_ids': fields.one2many('pos.payment', 'order_id', 'Order Payments', states={'draft':[('readonly',False)]}, readonly=True),
		'pricelist_id':fields.many2one('product.pricelist', 'Pricelist', required=True, states={'draft':[('readonly',False)]}, readonly=True),
		'partner_id':fields.many2one('res.partner', 'Partner',change_default=True, relate=True, states={'done':[('invoiced',True)]}),
		'journal_id': fields.selection(_journal_get, "Journal",size=32, states={'draft':[('readonly',False)]}, readonly=True),
#		'journal_id': fields.many2one('account.journal', "Journal",states={'done':[('readonly',True)]}),

 		'payment_amount': fields.float('Paid', states={'draft':[('readonly',False)]}, readonly=True),

  		'payment_return': fields.function(_payment_return, method=True, string='Return'),
 		'left_to_pay': fields.function(_left_to_pay, method=True, string='Left to pay'  ),
 		'state': fields.selection([('draft','Draft'),('done','Done'),('invoiced','Invoiced')], 'State',readonly=True),

		'invoice_id': fields.many2one('account.invoice', 'Invoice' , readonly=True),
		'picking_id':fields.many2one('stock.picking','Picking', readonly=True),
		'note': fields.text('Notes'),
 		'nb_print': fields.integer('Number of print',readonly=True)
		}
	_order = "date_order desc"

	def _journal_default(self, cr, uid, context={}):
		journal_list = self.pool.get('account.journal').search(cr,uid,[('type','=','cash')])
		if journal_list:
			return journal_list[0]
		else :
			return False


	_defaults={
		'user_id': lambda self,cr,uid, context: uid,
		'state': lambda *a: 'draft',
		'name': lambda obj, cr, uid, context: obj.pool.get('ir.sequence').get(cr, uid, 'pos.order'),
		'journal_id': _journal_default,
		'date_order': lambda *a: time.strftime('%Y-%m-%d'),
		'date_validity': lambda *a: (DateTime.now() + DateTime.RelativeDateTime(months=+6)).strftime('%Y-%m-%d'),
		'payment_amount': lambda *a: 0,
		'nb_print': lambda *a: 0,
		}

	def button_dummy(self, cr, uid, ids, context={}):
		for order in  self.browse(cr, uid, ids):
			if order.payment_amount == 0.0 or order.payment_amount < order.amount_total:
				self.write(cr, uid, [order.id], {
					'payment_amount':order._amount_total(cr, uid, ids, field_name="",arg={},context=context)[order.id]})
		return True


	def button_ok_complex(self, cr, uid, ids, context={}):

		for order in self.browse(cr, uid, ids):
			self.test_order_lines(cr, uid, ids, order,context)
			if not order.payment_ids :
				raise osv.except_osv("Error","No payment defined for this sale.")
			i=1
			tot= 0
			for payment in order.payment_ids:
				if not payment.journal_id :
					raise osv.except_osv("Error","No journal defined for the payment line %d" % (i,))
				if not payment.amount :
					raise osv.except_osv("Error","No amount defined for the payment line %d." % (i,))
				i+=1
				tot+= payment.amount

			if abs(float(tot)) - abs(float(order.amount_total)) > 10**-6:
				raise osv.except_osv("Error","The amount paid does not match the total amount")
			self.create_picking(cr, uid, ids, order,context)
		return True

	def button_ok_simple(self, cr, uid, ids, context={}):

		# verif du compte + creation des picking :
		for order in self.browse(cr, uid, ids):

			self.test_order_lines(cr, uid, ids, order,context)
			if not order.journal_id :
				raise osv.except_osv("Error","Please choose a journal for the sale ("+order.name+").")
			self.create_picking(cr, uid, ids, order,context)

		return True

	def test_order_lines(self, cr, uid,ids,order,context={}):
		if not order.order_line :
			raise osv.except_osv("Error","No order lines defined for this sale.")
			return False
		i=1
 		for line in order.order_line :
			if not line.product_id :
				raise osv.except_osv("Error","No product for the order line %d." % (i,))
				return False
			i+=1
		return True

	def create_picking(self, cr, uid,ids,order,context={}):

		picking_id = self.pool.get('stock.picking').create(cr, uid, {
			'name':'POS picking',
			'origin': 'POS %s' % order.id,
			'type': 'out',
			'state': 'draft',
			'move_type': 'direct',
			'note': 'POS notes '+ (order.note or ""),
			'invoice_state': 'none',
			'auto_picking': True,
			})
		self.write(cr, uid, [order.id], {'picking_id': picking_id})

		for line in  order.order_line:
			prop_ids=  self.pool.get("ir.property").search(cr, uid, [('name','=','property_stock_customer')])
			val = self.pool.get("ir.property").browse(cr,uid,prop_ids[0]).value
			location_id= order.shop_id.warehouse_id.lot_stock_id.id
			stock_dest_id = int(val.split(',')[1])
			if line.qty < 0 :
				(location_id,stock_dest_id)= (stock_dest_id,location_id)

			self.pool.get('stock.move').create(cr, uid, {
				'name':'Stock move (POS %d)'% (order.id,),
				'product_uom': line.product_id.uom_id.id,
				'picking_id': picking_id,
				'product_id': line.product_id.id,
				'product_uos_qty': line.qty,
				'tracking_id': False,
				'state': 'waiting',
				'location_id': location_id,
				'location_dest_id': stock_dest_id,
			})

		self.wf_service.trg_validate(uid, 'stock.picking', picking_id, 'button_confirm', cr)
		self.pool.get('stock.picking').force_assign(cr, uid, [picking_id], context)
		
		#self.wf_service.trg_validate(uid, 'stock.picking', picking_id, 'force_assign', cr)

		return self.write(cr, uid, ids, {'state':'done'})

	def refund(self, cr, uid, ids, context={}):
		clone_list=[]
		line_obj= self.pool.get('pos.order.line')

		for order in self.browse(cr, uid, ids):
			clone_id = self.copy(cr, uid, order.id, {
				'name': order.name + ' REFUND',
				'date_order': time.strftime('%Y-%m-%d'),
				'state':'draft',
				'note':'REFUND\n'+ (order.note or ''),
				'invoice_id': False,
				'nb_print': 0,
				})
			clone_list.append(clone_id)


		for clone in self.browse(cr, uid, clone_list):
			for order_line in clone.order_line:
				line_obj.write(cr, uid, [order_line.id], {'qty': -order_line.qty})
		return clone_list


	def create_invoice(self, cr, uid, ids, context={}):

		inv_ref= self.pool.get('account.invoice')
		inv_line_ref= self.pool.get('account.invoice.line')
		inv_ids=[]

		for order in  self.browse(cr, uid,ids, context):

			if order.invoice_id:
				inv_ids.append(order.invoice_id.id)
				continue

			if not order.partner_id:
				raise osv.except_osv('Error', 'Please provide a partner for the sale.')

			inv = {
				'name': 'Invoice for POS order: '+order.name,
				'origin': order.name,
				'type': 'out_invoice',
				'reference': "P%dPOS:%d"%(order.partner_id.id,order.id),
				'partner_id': order.partner_id.id,
				'comment': order.note or '',
				'price_type': 'tax_included'
				}
			inv.update(inv_ref.onchange_partner_id(cr,uid, [], 'out_invoice', order.partner_id.id)['value'])
			inv['account_id'] = inv['account_id'] and inv['account_id'][0]
			inv_id = inv_ref.create(cr, uid, inv, context)

			self.write(cr,uid,[order.id],{'invoice_id':inv_id, 'state':'invoiced'})
			inv_ids.append(inv_id)

			for line in order.order_line:
				inv_line= {
					'invoice_id': inv_id,
					'product_id': line.product_id.id,
					'quantity': line.qty,
					}
				inv_line.update(inv_line_ref.product_id_change(cr, uid,[],
															   line.product_id.id,
															   line.product_id.uom_id.id,
															   line.qty)['value'])
				inv_line['invoice_line_tax_id'] = ('invoice_line_tax_id' in inv_line) and [(6,0,inv_line['invoice_line_tax_id'])] or []
				inv_line_ref.create(cr, uid, inv_line,context)
		cr.commit()
		for i in inv_ids :  self.wf_service.trg_validate(uid, 'account.invoice',i , 'invoice_open', cr)
		return inv_ids

pos_order()



class pos_order_line(osv.osv):
	_name = "pos.order.line"
	_description = "Lines of Point of Sale"

	def _amount_line(self, cr, uid, ids, field_name, arg, context):
		res = {}
		for line in self.browse(cr, uid, ids):
			res[line.id] = line.price_unit * line.qty * (1 - (line.discount or 0.0) / 100.0)
		return res


	def onchange_product_id(self, cr, uid, ids, pricelist, product_id, qty=0, partner_id=False):

		if not product_id:
			return {'value': {'price_unit': 0.0} }
		if not pricelist:
			raise osv.except_osv('No Pricelist !', 'You have to select a pricelist in the sale form !\nPlease set one before choosing a product.')

		price = self.pool.get('product.pricelist').price_get(cr,uid,[pricelist], product_id, qty or 1.0, partner_id)[pricelist]
		if price is False:
			raise osv.except_osv('No valid pricelist line found !', "Couldn't find a pricelist line matching this product and quantity.\nYou have to change either the product, the quantity or the pricelist.")

		return {'value': {'price_unit': price}}


	_columns = {
		'name': fields.char('Line Description', size=8),
		'product_id': fields.many2one('product.product', 'Product', domain=[('sale_ok','=',True)], required=True,
									  change_default=True, relate=True),
		'price_unit': fields.float('Unit Price', required=True),
		'qty': fields.float('Quantity'),
 		'price_subtotal': fields.function(_amount_line, method=True, string='Subtotal'),
		'discount': fields.float('Discount (%)', digits=(16,2)),
		'order_id': fields.many2one('pos.order', 'Order Ref', ondelete='cascade'),
		'create_date': fields.datetime('Creation date', readonly=True),
		}
	_defaults = {
		'name': lambda obj, cr, uid, context: obj.pool.get('ir.sequence').get(cr, uid, 'pos.order.line'),
		'qty': lambda *a: 1,
		'discount': lambda *a: 0.0,
		}


 	def create(self, cr, user, vals, context={}):
 		if vals.get('product_id'):
 			return super(pos_order_line, self).create(cr, user, vals, context)
		return False
 	def write(self, cr, user, ids, values, context={}):
		if values.has_key('product_id') and not values['product_id']: return False
		return super(pos_order_line, self).write(cr, user, ids, values, context)

pos_order_line()



class pos_payment(osv.osv):
	_name = 'pos.payment'
	_description = 'Pos Payment'

	def _journal_get(self, cr, uid, context={}):
		obj = self.pool.get('account.journal')
		ids = obj.search(cr, uid, [('type','=','cash')])
		res = obj.read(cr, uid, ids, ['id', 'name'], context)
		res = [(r['id'], r['name']) for r in res]
		return res

	def _journal_default(self, cr, uid, context={}):
		journal_list = self.pool.get('account.journal').search(cr,uid,[('type','=','cash')])
		if journal_list:
			return journal_list[0]
		else :
			return False


	_columns = {
		'name': fields.char('Description', size=64),
		'order_id': fields.many2one('pos.order', 'Order Ref', required=True),
		'journal_id': fields.many2one('account.journal', "Journal", required=True),
		'amount': fields.float('Amount', required=True),
	}
	_defaults = {
		'name': lambda obj, cr, uid, context: obj.pool.get('ir.sequence').get(cr, uid, 'pos.payment'),
		'journal_id': _journal_default,
	}

 	def create(self, cr, user, vals, context={}):
 		if vals.get('journal_id') and vals.get('amount'):
 			return super(pos_payment, self).create(cr, user, vals, context)
		return False
 	def write(self, cr, user, ids, values, context={}):
		if values.has_key('amount') and not values['amount']: return False
		if values.has_key('journal_id') and not values['journal_id']: return False		
		return super(pos_payment, self).write(cr, user, ids, values, context)

pos_payment()


class report_transaction_pos(osv.osv):
    _name = "report.transaction.pos"
    _description = "transaction for the pos"
    _auto = False
    _columns = {
        'create_date': fields.date('Date', readonly=True),
        'journal_id':fields.many2one('account.journal', 'Journal', readonly=True, relate=True),
        'user_id':fields.many2one('res.users', 'User', readonly=True, relate=True),
        'no_trans': fields.float('Number of transaction', readonly=True),
        'amount': fields.float('Amount', readonly=True),
    }

    def init(self, cr):
        cr.execute("""
            create or replace view report_transaction_pos as (
                select
				  min(pp.id) as id,
  				  count(pp.id) as no_trans,
  				  sum(amount) as amount,
  				  pp.journal_id,
  				  to_char(pp.create_date, 'YYYY-MM-DD') as create_date,
  			      ps.user_id
 				from
  				  pos_payment pp left join pos_order ps on (ps.id = pp.order_id)
 				  group by
  					pp.journal_id, to_char(pp.create_date, 'YYYY-MM-DD'), ps.user_id
            )
        """)
report_transaction_pos()




