from osv import fields,osv
from osv import orm

class questionnaire(osv.osv):
	_name="crm_profiling.questionnaire"
	_description= "Questionnaire"
	_columns={
		'name': fields.char("Questionnaire",size=128, required=True),
		'description':fields.char("Description",size=128, required=True),
		}
questionnaire()

class question(osv.osv):
	_name="crm_profiling.question"
	_description= "Question"
	_columns={
		'name': fields.char("Question",size=128, required=True),
		'answers_ids': fields.one2many("crm_profiling.answer","question_id","Avalaible answers",),
		'questionnaire_id': fields.many2one('crm_profiling.questionnaire',"Questionnaire"),
		}
question()

class answer(osv.osv):
	_name="crm_profiling.answer"
	_description="Answer"
	_columns={
		"name": fields.char("Answer",size=128, required=True),
		"question_id": fields.many2one('crm_profiling.question',"Question"),
		}
answer()


class profile(osv.osv):
	_name="crm_profiling.profile"
	_description="Profile"
#	_inherits="res.partner.category"
	_columns={
		"name": fields.char("Description",size=128, required=True),
		"answer_yes": fields.many2many("crm_profiling.answer","profile_question_yes_rel","profile","answer","Inclued answers"),
		"answer_no": fields.many2many("crm_profiling.answer","profile_question_no_rel","profile","answer","Excluded answers"),
		'parent_id': fields.many2one('crm_profiling.profile', 'Parent profile'),
		'child_ids': fields.one2many('crm_profiling.profile', 'parent_id', 'Childs Profile'),
#		'cat_id': fields.one2one('res.partner.category','name'),
		'cat_id': fields.char('Category name', size=128)
		}
	_constraints = [
		(orm.orm.check_recursion, 'Error ! You can not create recursive profiles.', ['parent_id'])
	]

profile()

class partner(osv.osv):
	_inherit="res.partner"
	_columns={
		"answers_ids": fields.many2many("crm_profiling.answer","partner_question_rel","partner","answer","Answers"),
		}
partner()
