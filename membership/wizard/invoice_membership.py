from osv import fields
import wizard
import pooler
import time

def _invoice_membership(self, cr, uid, data, context):
	partner_id = data['id']
	product_id = data['form']['product']
	partner_address_id = data['form']['address']

	pool = pooler.get_pool(cr.dbname)

	invoice_obj = pool.get('account.invoice')
	invoice_id = invoice_obj.create(cr, uid, {
		'partner_id' : partner_id,
		'address_invoice_id': partner_address_id,
		'account_id': 1,
		}
	)

	invoice_line_obj = pool.get(('account.invoice.line'))
	invoice_line_id = invoice_line_obj.create(cr, uid, {
		'invoice_id' : invoice_id,
		'product_id' : product_id,
		'name' : 'test',
		'account_id': 1,
		}
	)
	print invoice_line_id


#	cr.execute('''
##		SELECT il.invoice_id
##		FROM account_invoice_line il
##		WHERE il.id IN (
##			SELECT ml.account_invoice_line
##			FROM membership_membership_line ml
##			WHERE ml.partner = %d
##			)
##		''' % partner_id)
##	invoices =  [x[0] for x in cr.fetchall()]

	value = {
			'domain': [
				('id', '=', invoice_id),
				('partner_id', '=', partner_id),
				('address_id', '=', partner_address_id),
				],
			'name': 'Membership invoice',
			'view_type': 'form',
			'view_mode': 'form',
			'res_model': 'account.invoice',
			'type': 'ir.actions.act_window',
		}

	print value
	return value

wizard_arch= """<?xml version="1.0"?>
<form string="Choose invoice details">
	<field
		name="product"
		domain="[('membership','=','True')]"
		/>
	<field
		name="address"
		domain="[('partner_id','=', 3)]"
		/>
</form>"""



class wizard_invoice_membership(wizard.interface):

	states = {
		
		'init' : {
			'actions' : [],
			'result' : {
				'type' : 'form',
				'arch' : wizard_arch,
				'fields' : {
						'product': {
							'string': 'Membership product',
							'type': 'many2one',
							'relation': 'product.product',
							'required': True
							},
						'address' : {
							'string': 'Invoicing address',
							'type': 'many2one',
							'relation': 'res.partner.address',
							'required': True
							},

						},
				    'state' : [('end', 'Cancel'),('ok', 'Confirm') ]}
		},

		'ok' : {
			'actions' : [],
			'result' : {'type' : 'action',
						'action': _invoice_membership,
						'state' : 'end'
			},
		},

	}

wizard_invoice_membership("wizard_invoice_membership")

