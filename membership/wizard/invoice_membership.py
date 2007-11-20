from osv import fields
import wizard
import pooler
import time

def _invoice_membership(self, cr, uid, data, context):
	partner_ids = data['ids']
	product_id = data['form']['product']

	pool = pooler.get_pool(cr.dbname)
	
	cr.execute('''
			SELECT partner_id, id, type
			FROM res_partner_address
			WHERE partner_id IN (%s)
			''' % ','.join([str(id) for id in partner_ids])
			)
	fetchal = cr.fetchall()
	partner_address_ids = {}
	for x in range(len(fetchal)):
		pid = fetchal[x][0]
		id = fetchal[x][1]
		type = fetchal[x][2]
		
		if partner_address_ids.has_key(pid) and partner_address_ids[pid]['type'] == 'invoice':
			continue
		partner_address_ids[pid] = {'id': id, 'type': type}
		

	invoice_list= []
	invoice_obj = pool.get('account.invoice')
	partner_obj = pool.get('res.partner')
	invoice_line_obj = pool.get(('account.invoice.line'))
	for partner_id in partner_ids:
		account_id = partner_obj.read(cr, uid, partner_id, ['property_account_receivable'])['property_account_receivable'][0]
		invoice_id = invoice_obj.create(cr, uid, {
			'partner_id' : partner_id,
			'address_invoice_id': partner_address_ids[partner_id]['id'],
			'account_id': account_id,
			}
		)
		invoice_line_id = invoice_line_obj.create(cr, uid, {
			'invoice_id' : invoice_id,
			'product_id' : product_id,
			'name' : 'test',
			'account_id': account_id,
			}
		)
		invoice_list.append(invoice_id)

	value = {
			'domain': [
				('id', 'in', invoice_list),
				],
			'name': 'Membership invoice',
			'view_type': 'form',
			'view_mode': 'tree,form',
			'res_model': 'account.invoice',
			'type': 'ir.actions.act_window',
		}

	return value

wizard_arch= """<?xml version="1.0"?>
<form string="Choose invoice details">
	<field
		name="product"
		domain="[('membership','=','True')]"
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

