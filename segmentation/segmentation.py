# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution	
#    Copyright (C) 2004-2008 Tiny SPRL (<http://tiny.be>). All Rights Reserved
#    $Id$
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from osv import fields,osv
from osv import orm
import pooler


def test_prof(self, cr, uid, prof_id, pid, answers_ids):
#return True if the partner pid fetch the profile rule prof_id
    ids_to_check = pooler.get_pool(cr.dbname).get('segmentation.profile').get_parents(cr, uid, [prof_id])
    [yes_answers, no_answers] = pooler.get_pool(cr.dbname).get('segmentation.profile').get_answers(cr, uid, ids_to_check)
    temp = True
    for y_ans in yes_answers:
        if y_ans not in answers_ids:
            temp = False
            break
    if temp:
        for ans in answers_ids:
            if ans in no_answers:
                temp = False
                break
    if temp:
        return True
    return False


def _recompute_profiles(self, cr, uid, pid, answers_ids):
    ok =  []

    cr.execute('''
        select id 
        from segmentation_profile
        order by id''')

    for prof_id in cr.fetchall():
        if test_prof(self, cr, uid, prof_id[0], pid, answers_ids):
            ok.append(prof_id[0])
    return ok

class question(osv.osv):
    _name="segmentation.question"
    _description= "Question"
    _columns={
        'name': fields.char("Question",size=128, required=True),
        'answers_ids': fields.one2many("segmentation.answer","question_id","Avalaible answers",),
        }
question()


class answer(osv.osv):
    _name="segmentation.answer"
    _description="Answer"
    _columns={
        "name": fields.char("Answer",size=128, required=True),
        "question_id": fields.many2one('segmentation.question',"Question"),
        }
answer()


class questionnaire(osv.osv):
    _name="segmentation.questionnaire"
    _description= "Questionnaire"
    _columns={
        'name': fields.char("Questionnaire",size=128, required=True),
        'description':fields.text("Description", required=True),
        'questions_ids': fields.many2many('segmentation.question','profile_questionnaire_quest_rel','questionnaire', 'question', "Questions"),
        }
questionnaire()


class profile(osv.osv):

    def get_answers(self, cr, uid, ids):
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

    def get_parents(self, cr, uid, ids):
        ids_to_check = ids
        cr.execute("""
         select distinct(parent_id)
         from segmentation_profile
         where parent_id is not null
         and id in (%s)""" % ','.join([str(i) for i in ids ]))

        parent_ids = [x[0] for x in cr.fetchall()]

        trigger = False
        for x in parent_ids:
            if x not in ids_to_check:
                ids_to_check.append(x)
                trigger = True

        if trigger:
            ids_to_check = pooler.get_pool(cr.dbname).get('segmentation.profile').get_parents(cr, uid, ids_to_check)

        return ids_to_check

    def process_continue(self, cr, uid, ids, state=False):
        cr.execute('delete from partner_profile_rel where profile_id=%s', (ids[0],))

        cr.execute('select id from res_partner order by id ')
        partners = [x[0] for x in cr.fetchall()]
        to_remove_list=[]
        for pid in partners:

            cr.execute('select distinct(answer) from partner_question_rel where partner=%s' % pid)
            answers_ids = [x[0] for x in cr.fetchall()]
            if (not test_prof(self, cr, uid, ids[0], pid, answers_ids)):
                to_remove_list.append(pid)

        for pid in to_remove_list:
            partners.remove(pid)

        for partner_id in partners:
            cr.execute('insert into partner_profile_rel (profile_id,partner_id) values (%s,%s)', (ids[0],partner_id))
        cr.commit()

        cr.commit()
        return True

    _name="segmentation.profile"
    _description="Profile"
    _columns={
        "name": fields.char("Description",size=128, required=True),
        "answer_yes": fields.many2many("segmentation.answer","profile_question_yes_rel","profile","answer","Inclued Answers"),
        "answer_no": fields.many2many("segmentation.answer","profile_question_no_rel","profile","answer","Excluded Answers"),
        'parent_id': fields.many2one('segmentation.profile', 'Parent Profile'),
        'child_ids': fields.one2many('segmentation.profile', 'parent_id', 'Childs Profile'),
        }
    _constraints = [
        (orm.orm.check_recursion, 'Error ! You can not create recursive profiles.', ['parent_id'])
    ]
profile()


class partner(osv.osv):

    def write(self, cr, uid, ids, vals, context=None):
        if not context:
            context={}
        if 'answers_ids' in vals:
            vals['profiles_ids']=[[6, 0, _recompute_profiles(self, cr, uid, ids[0],vals['answers_ids'][0][2])]]
        return super(partner, self).write(cr, uid, ids, vals, context=context)

    _inherit="res.partner"
    _columns={
        "answers_ids": fields.many2many("segmentation.answer","partner_question_rel","partner","answer","Answers"),
        "profiles_ids":fields.many2many("segmentation.profile","partner_profile_rel","partner_id","profile_id","Matching Profiles", readonly=True, select="2"),
        }
partner()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

