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

import wizard
import pooler

from tools import UpdateableStr, UpdateableDict
from tools.translate import _

#
# Poll form
#

_POLL_FORM = UpdateableStr()
_POLL_FIELDS = UpdateableDict()

_mess_form = """<?xml version="1.0"?>
<form string="Ended questionnaire">
 <field name="message" colspan="4" width="350" nolabel="1" />
</form>"""

_mess_fields = {
    'message': {
        'string': 'Question',
        'type': 'char',
        'size': 128,
        'readonly': True,
    },
}


class direct_poll(wizard.interface):
    def first(self, cr, uid, data, context):
        # Select the first question
        questionnaire = data['form']['questionnaire_name']
        quest_obj =  pooler.get_pool(cr.dbname).get('crm_profiling.questionnaire')
        first_id = quest_obj.read(cr, uid, questionnaire, ['first'], context)
        if not first_id['first']:
            raise wizard.except_wizard(_('Attention'), _('No first question defined on a questionnaire'))

        x_form, x_fields = self.build_form(cr, uid, first_id['first'], context)
        _POLL_FORM.__init__(x_form)
        _POLL_FIELDS.__init__(x_fields)
        return {}

    def check(self, cr, uid, data, context):
        answer = data['form']['answer']
        action = 'next'

        # Store the result on partner
        temp = []
        temp.append(answer)
        crm_obj = pooler.get_pool(cr.dbname).get('crm.case')
        partner = crm_obj.read(cr, uid, data['id'], ['partner_id'], context)
        partner_id = partner['partner_id'][0]

        query = "select answer from partner_question_rel where partner=%s"
        cr.execute(query, (partner_id,))
        for x in cr.fetchall():
            temp.append(x[0])

        partner_obj = pooler.get_pool(cr.dbname).get('res.partner')
        partner_obj.write(cr, uid, [partner_id],{'answers_ids':[[6,0,temp]]}, context)

        # Check if the last answer attached to a new question.
        answer_obj = pooler.get_pool(cr.dbname).get('crm_profiling.answer')
        next_id = answer_obj.read(cr, uid, answer, ['next'], context)
        if not next_id['next']:
            action = 'message'
        return action

    def next(self, cr , uid, data, context):
        answer = data['form']['answer']
        answer_obj = pooler.get_pool(cr.dbname).get('crm_profiling.answer')
        next_id = answer_obj.read(cr, uid, answer, ['next'], context)
        if not next_id:
            raise wizard.except_wizard(_('Error'), _('An error unknown'))

        x_form, x_fields = self.build_form(cr, uid, next_id['next'], context)
        _POLL_FORM.__init__(x_form)
        _POLL_FIELDS.__init__(x_fields)
        return {}

    def build_form(self, cr, uid, question, context):
        _form = """<?xml version="1.0"?>
<form string="%s">
 <field name="answer" colspan="4" domain="[('question_id','=',%s)]"/>
</form>""" % (question[1], str(question[0]))

        _fields = {'answer': {
                'string':'Answer',
                'type': 'many2one',
                'relation': 'crm_profiling.answer',
                'required': True,}
        }

        return _form, _fields

    def thanks(self, cr, uid, data, context):
        return {'message': _('The questionnaire is finished'),}

    _questionnaire_choice_arch = '''<?xml version="1.0"?>
    <form string="Questionnaire">
        <field name="questionnaire_name"/>
    </form>'''

    _questionnaire_choice_fields = {
            'questionnaire_name': {'string': 'Questionnaire name', 'type': 'many2one', 'relation': 'crm_profiling.questionnaire', 'required': True },
    }

    states = {
        'init': {
            'actions': [],
            'result': {
                'type': 'form', 
                'arch': _questionnaire_choice_arch, 
                'fields': _questionnaire_choice_fields, 
                'state':[('end', 'Cancel'), ('first', 'Open Questionnaire')]
            }
        },
        'first': {
            'actions': [first],
            'result': {
                'type': 'form',
                'arch': _POLL_FORM,
                'fields': _POLL_FIELDS,
                'state': [('end','Cancel', 'gtk-cancel'), ('check', 'Next', 'gtk-go-forward')]
            },
        },
        'next': {
            'actions': [next],
            'result': {
                'type': 'form',
                'arch': _POLL_FORM,
                'fields': _POLL_FIELDS,
                'state': [('end','Cancel', 'gtk-cancel'), ('check', 'Next', 'gtk-go-forward')]
            },
        },
        'check': {
            'actions': [],
            'result': {
                'type': 'choice',
                'next_state': check,
            },
        },
        'message': {
            'actions': [],
            'result': {
                'type': 'form', 
                'arch': _mess_form, 
                'fields': _mess_fields, 
                'state':[('end', 'End')]
            }
        },

    }

direct_poll('crm.direct_poll')

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
