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
import pooler
import wizard
from tools import UpdateableStr, UpdateableDict

_QUEST_FORM = UpdateableStr()
_QUEST_FIELDS=UpdateableDict()

class open_questionnaire(wizard.interface):

    def _questionnaire_compute(self, cr, uid, data, context):
        temp = []   
        for x in data['form']:
            if x[:len(x)-1] == "quest_form" and data['form'][x] != 0 :
                
                temp.append(data['form'][x])

        query = """ 
        select answer from partner_question_rel 
        where partner =%d"""% data['id']
        cr.execute(query)
        for x in cr.fetchall():
            temp.append(x[0])

        pooler.get_pool(cr.dbname).get('res.partner').write(cr, uid, [data['id']],{'answers_ids':[[6,0,temp]]}, context )
        return {}


    def build_form(self, cr, uid, data, context):
        query = """
        select name, id
        from segmentation_question
        where id in ( select question from profile_questionnaire_quest_rel where questionnaire = %s)"""% data['form']['questionnaire_name']
        cr.execute(query)
        
        quest_fields={}
        quest_form='''<?xml version="1.0"?>
            <form string="Questionnaire">'''
        
        for x in cr.fetchall():
            quest_form = quest_form + '''<field name="quest_form'''+str(x[1])+'''"/><newline/>'''
            quest_fields['quest_form'+str(x[1])] = {'string': str(x[0]), 'type': 'many2one', 'relation': 'segmentation.answer', 'domain': [('question_id','=',x[1])] }
        quest_form = quest_form + '''</form>'''      
        _QUEST_FORM. __init__(quest_form)
        _QUEST_FIELDS.__init__(quest_fields)
        return {}

    _questionnaire_choice_arch = '''<?xml version="1.0"?>
    <form string="Questionnaire">
        <field name="questionnaire_name"/>
    </form>'''

    _questionnaire_choice_fields = {
            'questionnaire_name': {'string': 'Questionnaire name', 'type': 'many2one', 'relation': 'segmentation.questionnaire', 'required': True },
    }

    states = {
        'init': {
            'actions': [],
            'result': {'type': 'form', 'arch': _questionnaire_choice_arch, 'fields': _questionnaire_choice_fields, 'state':[('end', 'Cancel'), ('open', 'Open Questionnaire')]}
        },
        'open': {
            'actions': [build_form],
            'result': {'type': 'form', 'arch':_QUEST_FORM, 'fields': _QUEST_FIELDS, 'state':[('end', 'Cancel'), ('compute', 'Save Data')]}
        },
        'compute': {
            'actions': [],
            'result': {'type': 'action', 'action': _questionnaire_compute, 'state':'end'}
        }
    }

open_questionnaire('open_questionnaire')
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

