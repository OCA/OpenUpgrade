from osv import fields,osv

class question(osv.osv):
	_name="segmentation.question"
	_description= "Question"
	_columns={
		'name': fields.char("Question",size=128),
		}
question()

class answer(osv.osv):
	_name="segmentation.answer"
	_description="Answer"
	_columns={
		"question": fields.many2one('segmentation.question',"Question"),
		"name": fields.char("Answer",size=128),
		}
answer()


class profile(osv.osv):
	def _check_recursion(self, cr, uid, ids):
		level = 100
		while len(ids):
			cr.execute('select distinct parent_id from segmentation_profile where id in ('+','.join(map(str,ids))+')')
			ids = filter(None, map(lambda x:x[0], cr.fetchall()))
			if not level:
				return False
			level -= 1
		return True
	_name="segmentation.profile"
	_description="Profile"
	_columns={
		"name": fields.char("Description",size=128),
		"answer_yes": fields.many2many("segmentation.answer","profile_question_yes_rel","profile","answer","Inclued answers"),
		"answer_no": fields.many2many("segmentation.answer","profile_question_no_rel","profile","answer","Excluded answers"),
		'parent_id': fields.many2one('segmentation.profile', 'Inherits from'),
		'child_ids': fields.one2many('segmentation.profile', 'parent_id', 'Childs Profile'),
		}
	_constraints = [
		(_check_recursion, 'Error ! You can not create recursive profiles.', ['parent_id'])
	]

profile()

class partner(osv.osv): 
	_inherit="res.partner"
	_columns={
		"anwers": fields.many2many("segmentation.answer","partner_question_rel","partner","answer","Answers"),
		}
partner()
