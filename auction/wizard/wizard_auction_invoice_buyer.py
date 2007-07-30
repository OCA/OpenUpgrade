
import wizard
import netsvc
import pooler

invoice_form = '''<?xml version="1.0"?>
<form title="Paid ?">
	<field name="amount"/>
	<field name="objects"/>
	<field name="number"/>
	<label string="(Keep empty for automatic number)" colspan="2"/>
</form>'''

invoice_fields = {
	'amount': {'string':'Invoiced Amount', 'type':'float', 'required':True, 'readonly':True},
	'objects': {'string':'# of objects', 'type':'integer', 'required':True, 'readonly':True},
	'number': {'string':'Invoice Number', 'type':'integer'},
}


def _values(self,cr,uid, datas,context={}):
	lots= pooler.get_pool(cr.dbname).get('auction.lots').browse(cr,uid,datas['ids'])
	price = 0.0
	amount_total=0.0
	pt_tax=pooler.get_pool(cr.dbname).get('account.tax')
	for lot in lots:
		taxes = lot.product_id.taxes_id
		if lot.author_right:
			taxes.append(lot.author_right)
		else:
			taxes += lot.auction_id.buyer_costs
		tax=pt_tax.compute(cr,uid,taxes,lot.obj_price,1)
		for t in tax:
			amount_total+=t['amount']
		amount_total+=lot.obj_price
	invoice_number = False
	return {'objects':len(datas['ids']), 'amount':amount_total, 'number':invoice_number}


def _makeInvoices(self, cr, uid, data, context):
	order_obj = pooler.get_pool(cr.dbname).get('auction.lots')
	newinv = []
	ids = order_obj.lots_invoice(cr, uid, data['ids'],context)
	cr.commit()
	return {
		'domain': "[('id','in', ["+','.join(map(str,ids))+"])]",
		'name': 'Buyer invoices',
		'view_type': 'form',
		'view_mode': 'tree,form',
		'res_model': 'account.invoice',
		'view_id': False,
		'context': "{'type':'in_refund'}",
		'type': 'ir.actions.act_window'
	}
	return {}

class make_invoice(wizard.interface):
	states = {
		'init' : {
			'actions' : [_values],
			'result' : {'type' : 'form',
				    'arch' : invoice_form,
				    'fields' : invoice_fields,
				    'state' : [('invoice', 'Create invoices'), ('end', 'Cancel'),]}
		},
		'invoice' : {
			'actions' : [_makeInvoices],
			'result' : {'type' : 'action',
				    'action' : _makeInvoices,
				    'state' : 'end'}
		},
	}
make_invoice("auction.lots.make_invoice_buyer")
