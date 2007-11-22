import pooler
import wizard

def _open_partner(self, cr, uid, data, context):

	def _get_answers(self, cr, uid, ids):
		query = """
		select distinct(answer)
		from profile_question_yes_rel
		where profile in (%s)"""% ','.join([str(i) for i in ids ])

		cr.execute(query)
		ans_yes = [x[0] for x in cr.fetchall()]

		query = """
		select distinct(answer)
		from profile_question_no_rel
		where profile in (%s)"""% ','.join([str(i) for i in ids ])

		cr.execute(query)
		ans_no = [x[0] for x in cr.fetchall()]

		return [ans_yes, ans_no]

	def _get_parents(self, cr, uid, ids):
		ids_to_check = ids
		cr.execute("""
		 select distinct(parent_id)
		 from crm_profiling_profile
		 where parent_id is not null
		 and id in (%s)""" % ','.join([str(i) for i in ids ]))

		parent_ids = [x[0] for x in cr.fetchall()]

		trigger = False
		for x in parent_ids:
			if x not in ids_to_check:
				ids_to_check.append(x)
				trigger = True

		if trigger:
			ids_to_check = _get_parents(self, cr, uid, ids_to_check)

		return ids_to_check

	if (data['id'] in data['ids'])|(data['ids'] == []):
		ids_to_check = _get_parents(self, cr, uid, data['ids'])	
	else:		
		ids_to_check = _get_parents(self, cr, uid, [data['id']])

	[yes_answers, no_answers] = _get_answers(self, cr, uid, ids_to_check)

	query = "select partner from partner_question_rel "
	query_end =	"group by partner"

	if yes_answers != []:
		query = query + """
		where answer in (%s) """	% (','.join([str(a) for a in yes_answers]))	

		#rebuild the end of the query
		query_end =	"""
		group by partner
		having count(*) >= %s """ % len(yes_answers)

	if no_answers != []:
		if yes_answers != []:
			query = query + "and "
		else:
			query = query + "where "

		query = query + """
		partner not in (
			select partner from partner_question_rel 
			where answer in (%s)) """ % ( ','.join([str(a) for a in no_answers]))

	query = query + query_end
	cr.execute(query)
	
	action= {
		'name': 'Matching partners',
		'view_type': 'form',
		'view_mode': 'tree,form',
		'res_model': 'res.partner',
		'type': 'ir.actions.act_window'
		}

	(res,) =cr.fetchall(),
	if len(res)==1:
		action['domain']= "[('id','=',(%s))]" % str(res[0][0])
	else:
		action['domain']= "[('id','in',(%s))]" % ','.join([str(x[0]) for x in res])
		
	return action

class open_partner(wizard.interface):
	states = {
		'init': {
			'actions': [],
			'result': {'type': 'action', 'action': _open_partner, 'state':'end'}
		}
	}

open_partner('open_partner')
