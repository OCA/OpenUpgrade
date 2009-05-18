# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution	
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>). All Rights Reserved
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

from osv import osv, fields

class training_questionnaire(osv.osv):
    _name = 'training.questionnaire'
training_questionnaire()

class training_course(osv.osv):
    _inherit = 'training.course'

    _columns = {
        'questionnaire_ids' : fields.one2many('training.questionnaire',
                                              'course_id',
                                              'Questionnaire'),
    }

training_course()

class training_offer(osv.osv):
    _inherit = 'training.offer'
    _columns = {
        'questionnaire_ids' : fields.many2many('training.questionnaire',
                                               'training_questionnaire_offer_rel',
                                               'offer_id',
                                               'questionnaire_id',
                                               'Questionnaires'),
    }

training_offer()

class training_question(osv.osv):
    _name= 'training.question'
training_question()

class training_exam_answer(osv.osv):
    _name = 'training.exam_answer'
    _description = 'Answer'
    _columns = {
        'name' : fields.char('Response', size=128, required=True, select=1),
        'is_response' : fields.boolean('Correct Answer'),
        'question_id' : fields.many2one('training.question', 'Question', select=True, required=True),
    }
training_exam_answer()

class training_question(osv.osv):
    _name = 'training.question'
    _description = 'Question'
    _columns = {
        'name' : fields.text('Question', required=True, select=1),
        'kind' : fields.selection([('mandatory', 'Mandatory'),
                                   ('eliminatory', 'Eliminatory'),
                                   ('normal', 'Normal')
                                  ],
                                  'Kind', required=True, select=1),
        'type' : fields.selection([('plain', 'Plain'),
                                   ('qcm', 'QCM'),
                                   ('yesno', 'Yes/No')
                                  ],
                                  'Type',
                                  required=True,
                                  select=1 ),
        'response_plain' : fields.text('Response Plain'),
        'response_yesno' : fields.boolean('Response Yes/No'),
        'exam_answer_ids' : fields.one2many('training.exam_answer',
                                              'question_id',
                                              'Response QCM'),
        'questionnaire_ids': fields.many2many('training.questionnaire',
                                              'training_questionnaire_question_rel',
                                              'question_id',
                                              'questionnaire_id',
                                              'Questionnaire'),
    }

    _defaults = {
        'kind' : lambda *a: 'normal',
        'type' : lambda *a: 'plain',
        'response_yesno' : lambda *a: False,
    }

training_question()

class training_questionnaire(osv.osv):
    _name = 'training.questionnaire'
    _description = 'Questionnaire'

    _columns = {
        'name' : fields.char( 'Name', size=32, required=True, select=1 ),
        'course_id' : fields.many2one('training.course', 'Course'),
        'state' : fields.selection([('draft', 'Draft'),
                                    ('validated', 'Validated'),
                                    ('pending', 'Pending'),
                                    ('inprogress', 'In Progress'),
                                    ('deprecated', 'Deprecated')
                                   ],
                                   'State', required=True, readonly=True, select=1),
        'objective' : fields.text('Objective'),
        'description' : fields.text('Description'),
        'question_ids' : fields.many2many('training.question',
                                          'training_questionnaire_question_rel',
                                          'questionnaire_id',
                                          'question_id', 'Questions'),
    }

    _defaults = {
        'state' : lambda *a: 'draft',
    }

training_questionnaire()

class training_planned_exam(osv.osv):
    _name = 'training.planned_exam'
    _description = 'Planned Exam'
    _columns = {
        'name' : fields.char('Name', size=64, select=1, required=True),
        'date' : fields.datetime('Date', required=False, select=1),
        'duration' : fields.float('Duration', required=False, select=1),
        # 'location_id' : fields.many2one('training.location', 
        'state' : fields.selection([('draft', 'Draft'),
                                    ('opened', 'Opened'),
                                    ('opened_confirmed', 'Opened Confirmed'),
                                    ('closed_confirmed', 'Closed Confirmed'),
                                    ('inprogress', 'In Progress'),
                                    ('closed', 'Closed'),
                                    ('cancelled', 'Cancelled')],
                                   'State',
                                   required=True,
                                   readonly=True,
                                   select=1
                                  ),
        'participant_ids' : fields.many2many('training.subscription',
                                             'training_participation',
                                             'seance_id',
                                             'subscription_id',
                                             'Participants',
                                             domain="[('group_id', '=', group_id)]" ),
        'group_id' : fields.many2one('training.group', 'Group'),
        'contact_ids' : fields.many2many('res.partner.contact', 'planned_exam_contact_rel',
                                         'planned_exam_id', 'contact_id',
                                         'StakeHolder'),
        'questionnaire_id' : fields.many2one('training.questionnaire',
                                             'Questionnaire',
                                             required=True),
        'subscription_line_id' : fields.many2one('training.subscription.line', 'Subscription'),
    }

    _defaults = {
        'state' : lambda *a: 'draft',
    }

training_planned_exam()

class training_subscription_line(osv.osv):
    _inherit = 'training.subscription.line'
    _columns = {
        'with_exam' : fields.boolean('With Exam'),
        'exam_id' : fields.one2many('training.planned_exam', 'Planned Exam'),
    }
    _defaults = {
        'with_exam' : lambda *a: 0,
    }

training_subscription_line()

class training_exam_result(osv.osv):
    _name = 'training.exam.result'
    _description = 'exam Result'
    _columns = {
        'participation_id' : fields.many2one('training.participation', 'Participation',
                                             required=True),
        'exam_id' : fields.many2one('training.planned_exam', 'Exam',
                                    required=True),
    }

training_exam_result()

#class training_exam_result_line(osv.osv):
#    _name = 'training.exam.result.line'
#    _columns = {
#        'question_id' : fields.many2one('training.question', 'Question', required=True),
#    }
#
#training_exam_result_line()



# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
