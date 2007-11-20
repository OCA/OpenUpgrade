from osv import fields,osv
from osv import orm
class question(osv.osv):
	_name="segmentation.question"
	_description= "Question"
	_columns={
		'name': fields.char("Question",size=128, required=True),
		'answers': fields.one2many("segmentation.answer","question","Avalaible answers",),
		}
question()

class answer(osv.osv):
	_name="segmentation.answer"
	_description="Answer"
	_columns={
		"question": fields.many2one('segmentation.question',"Question"),
		"name": fields.char("Answer",size=128, required=True),
		}
answer()


class profile(osv.osv):

	_name="segmentation.profile"
	_description="Profile"
	_columns={
		"name": fields.char("Description",size=128, required=True),
		"answer_yes": fields.many2many("segmentation.answer","profile_question_yes_rel","profile","answer","Inclued answers"),
		"answer_no": fields.many2many("segmentation.answer","profile_question_no_rel","profile","answer","Excluded answers"),
		'parent_id': fields.many2one('segmentation.profile', 'Inherits from'),
		'child_ids': fields.one2many('segmentation.profile', 'parent_id', 'Childs Profile'),
		}
	_constraints = [
		(orm.orm.check_recursion, 'Error ! You can not create recursive profiles.', ['parent_id'])
	]

profile()

class partner(osv.osv):
	_inherit="res.partner"
	_columns={
		"answers": fields.many2many("segmentation.answer","partner_question_rel","partner","answer","Answers"),
		}
partner()
