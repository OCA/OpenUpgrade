
import wizard
import netsvc
import pooler



invoice_form = """<?xml version="1.0"?>
<form string="Create invoices">
	<separator colspan="4" string="Do you really want to create the invoices ?" />
	
</form>
"""

invoice_fields = {
	
}

ack_form = """<?xml version="1.0"?>
<form string="Create invoices">
	<separator string="Invoices created" />
</form>"""

ack_fields = {}

def _makeInvoices(self, cr, uid, data, context):
	order_obj = pooler.get_pool(cr.dbname).get('auction.lots')
	newinv = []
	ids = order_obj.seller_trans_create(cr, uid, data['ids'],context)
	cr.commit()
	return {
		'domain': "[('id','in', ["+','.join(map(str,ids))+"])]",
		'name': 'Seller invoices',
		'view_type': 'form',
		'view_mode': 'tree,form',
		'res_model': 'account.invoice',
		'view_id': False,
		'context': "{'type':'out_refund'}",
		'type': 'ir.actions.act_window'
	}
	return {}

class make_invoice(wizard.interface):
	states = {
		'init' : {
			'actions' : [],
			'result' : {'type' : 'form',
				    'arch' : invoice_form,
				    'fields' : invoice_fields,
				    'state' : [('end', 'Cancel'),('invoice', 'Create invoices') ]}
		},
		'invoice' : {
			'actions' : [_makeInvoices],
			'result' : {'type' : 'action',
				    'action' : _makeInvoices,
				    'state' : 'end'}
		},
	}
make_invoice("auction.lots.make_invoice")
