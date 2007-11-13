import wizard
import pooler

#
#wizard_arch= """<?xml version="1.0"?>
#<form string="title">
#<label string="Are you sure ?"/>
#</form>"""
#

def _event_registration(self, cr, uid, data, context):
	event_id = data['id']
	cr.execute('''
		SELECT c.id
		FROM crm_case c
		WHERE c.section_id IN (
			SELECT e.section_id
			FROM event_event e
			WHERE e.id = %d
			)
		'''% (event_id))

	ids = [x[0] for x in cr.fetchall()]
	print ids

	value = {
			'domain': [('id', 'in', ids)],
			'name': 'Event registration',
			'view_type': 'form',
			'view_mode': 'tree,form',
			'res_model': 'crm.case',
			'view_id': False,
			'context': {
				'section_id': event_id,
				},
			'type': 'ir.actions.act_window'
		}

	return value



class event_registration(wizard.interface):
	states = {
		
		'init': {
			'actions': [],
			'result': {
				'type': 'action',
				'action': _event_registration,
				'state': 'end'
						}
			},

	}
event_registration("event_registration")

