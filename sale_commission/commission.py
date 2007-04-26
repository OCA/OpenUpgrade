from osv import fields,osv

class report_commission_month(osv.osv):
	_name = "sale_commission.report.month"
	_description = "Commissions"
	_auto = False
	_columns = {
		'name': fields.date('Invoice Date', readonly=True),
		'saleagent_id': fields.many2one('sale.commission.agent', 'Saleagent',readonly=True),
		'sono':fields.integer('Sale order', readonly=True),
		'invno':fields.integer('Invoice Number', readonly=True),
		'product_quantity':fields.integer('Product Quantity', readonly=True),
		'product_id':fields.many2one('product.product', 'Product', readonly=True),
		'inv_total':fields.float('Invoice Amount', readonly=True),
		'comrate': fields.function(_commission_rate, method=True, string='Commission Rate (%)'),
		'commission': fields.function(_commission, method=True, string='Commissions Amount'),
		'pdate': fields.date('Invoice Paid Date', readonly=True),
		'state': fields.char('State',size=64, readonly=True),
	}
	_order = 'name,sono,state'
	def _commission_rate():
		result = {}
		for com in self.browse(cr, uid, ids, context):
			result[com.id] = 
	def _commission():
	def init(self, cr):
		print "In init of commision month ..";
		cr.execute("""create or replace view sale_commission_report_month as (
	select 
		min(l.id) is id,
		i.name as name,
		i.origin as sono,
		i.number as invno,
		sum(quantity) as product_quantity,
		l.product_id as product_id,
		sum(l.price_unit * (100-l.price_discount) * l.quantity) as inv_total,
		i.date as in_date,
		i.state as state
	from
		account_invoice_line l
		left join account_invoice i on (l.invoice_id=i.id)
		left join sale_commission_agent a on ()
		left join account_move m on (i.move_id=m.id)
	)""")
report_commission_month()

