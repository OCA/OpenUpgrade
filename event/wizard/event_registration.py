import wizard
import pooler

def _event_registration(self, cr, uid, data, context):
	event_id = data['id']
#	cr.execute('''
#	SELECT r.id FROM event_registration r WHERE r.section_id = %d
#		'''% (event_id))

#	ids = [x[0] for x in cr.fetchall()]

	value = {
			'domain': [('section_id', '=', event_id)],
			'name': 'Event registration',
			'view_type': 'form',
			'view_mode': 'tree,form',
			'res_model': 'event.registration',
			'context': {
				},
			'type': 'ir.actions.act_window'
		}

	return value



class wizard_event_registration(wizard.interface):
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
wizard_event_registration("wizard_event_registration")

