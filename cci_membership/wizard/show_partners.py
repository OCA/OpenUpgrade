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
import time
import datetime

form = """<?xml version="1.0"?>
<form string="Selecting Partners" colspan="4">
    <field name="select" />
</form>
"""

fields = {
    'select':{'string':'Select Criteria','type':'selection','selection':[('lines', 'Criteria about amount sold and membership state'),('crm','Criteria about registration to specified event')]},
}

lines_form = """<?xml version="1.0"?>
<form string="Select Criteria For Partners - Amount Sold" colspan="4">
    <label string="This wizard will help you selecting the partners that have/haven't spend more than the specified amount in the specified period." colspan="4" />
    <separator colspan="4"/>
    <field name="date_from" />
    <field name="date_to" />
    <field name="amount" />
    <field name="member_state" colspan="4" />
    <newline/>
    <field name="removing_from_list" />
</form>
"""

lines_fields = {
    'date_from': {'string':'Start of period', 'type':'date', 'required':True},
    'date_to': {'string':'End of period', 'type':'date', 'required':True, 'default': lambda *a: time.strftime('%Y-%m-%d')},
    'amount': {'string':'Amount', 'type':'float', 'required':True, 'default': lambda *a: 0.0},
    'member_state':{'string':'Current Membership state','type':'selection','selection':[('none', 'Non Member'),('canceled','Canceled Member'),('old','Old Member'),('waiting','Waiting Member'),('invoiced','Invoiced Member'),('free','Free Member'),('paid','Paid Member')],'required':True, 'help':'The wizard will only pay attention to partners in this membership state'},
    'removing_from_list': {'string':'Keep only fetching partners', 'type':'boolean', 'help': """The result will be a list of partner:
\n* Either only the fetching partners, if this box is checked.
\n* Otherwise, all the partners minus the ones that fetch the criteria."""},
}


crm_form = """<?xml version="1.0"?>
<form string="Select Criteria For Partners-CRM cases and sections" colspan="4">
    <label string="This wizard will help you selecting the partners that have/haven't participated to a specific event." colspan="4" />
    <separator colspan="4"/>
    <field name="section" domain="[('parent_id','child_of','Event')]" colspan="2"/>
    <field name="state" colspan="2"/>
    <newline/>
    <field name="removing_from_list" />
</form>
"""

crm_fields = {
    'section': {'string': 'Event', 'type': 'many2one', 'relation': 'crm.case.section','required':True, 'domain':"[('parent_id','like','Events')]",},
    'state':{'string':'State','type':'selection','selection':[('draft','Draft'),('open','Open'),('cancel', 'Cancel'),('done', 'Close'),('pending','Pending')],'required':True,'help':'The wizard will look if a partner has a registration of that specified state for the chosen event'},
    'removing_from_list': {'string':'Keep only fetching partners', 'type':'boolean', 'help': """The result will be a list of partner:
\n* Either only the fetching partners, if this box is checked.
\n* Otherwise, all the partners minus the ones that fetch the criteria."""},
}


class show_partners(wizard.interface):

    def _defaults(self, cr, uid, data, context):
        data['form']['select'] = 'lines'
        return data['form']

    def _defaults_lines(self, cr, uid, data, context):
        today = datetime.datetime.today()
        from_date = today - datetime.timedelta(30)
        data['form']['date_from'] = from_date.strftime('%Y-%m-%d')
        data['form']['member_state'] = 'free'
        return data['form']

    def _defaults_crm(self, cr, uid, data, context):
        data['form']['state'] = 'open'
        return data['form']

    def _check(self, cr, uid, data, context):
        if data['form']['select'] == 'crm':
            return 'crm'
        return 'entry_lines'


    def _open_window_selected_partners(self, cr, uid, data, context):
        mod_obj = pooler.get_pool(cr.dbname).get('ir.model.data')
        act_obj = pooler.get_pool(cr.dbname).get('ir.actions.act_window')

        result = mod_obj._get_id(cr, uid, 'base', 'action_partner_form')
        list_ids = []

        if data['form']['select'] == 'lines':
            if not data['form']['amount']:
                raise wizard.except_wizard('Warning','Amount should be greater than zero')
            cr.execute("select distinct(partner_id) from account_move_line where credit>=%f and (date between to_date(%s,'yyyy-mm-dd') and to_date(%s,'yyyy-mm-dd')) and (partner_id is not null)", (data['form']['amount'], data['form']['date_from'], data['form']['date_to']))
            entry_lines = cr.fetchall()

            entry_ids = [x[0] for x in  entry_lines]
            a_id = pooler.get_pool(cr.dbname).get('res.partner').read(cr, uid, entry_ids, ['membership_state'])

            for i in range(0, len(a_id)):
                if a_id[i]['membership_state'] == data['form']['member_state']:
                    list_ids.append(a_id[i]['id'])
        else:
            cr.execute("select distinct(partner_id),section_id,state from crm_case where section_id=%d and state=%s and (partner_id is not null)", (data['form']['section'], data['form']['state']))
            p_ids = cr.fetchall()
            list_ids = [x[0] for x in p_ids]


        id = mod_obj.read(cr, uid, [result], ['res_id'])[0]['res_id']
        result = act_obj.read(cr, uid, [id])[0]

        if data['form']['removing_from_list']:
            result['domain'] = [('id', 'in', list_ids)]
        else:
            result['domain'] = [('id', 'not in', list_ids)]
#       result['context'] = ({'id': entry_ids})
        return result

    states = {
        'init' : {
            'actions' : [_defaults],
            'result' : {'type' : 'form' , 'arch' : form,
                    'fields' : fields,
                    'state' : [('end', 'Cancel'), ('go', 'Go')]}
        },
        'go': {
            'actions': [],
            'result': {'type':'choice', 'next_state':_check}
        },
        'entry_lines': {
            'actions': [_defaults_lines],
            'result': {'type':'form', 'arch':lines_form, 'fields':lines_fields, 'state':[('end', 'Cancel'),('choose','Choose')]}
        },
        'crm': {
            'actions': [_defaults_crm],
            'result': {'type':'form', 'arch':crm_form, 'fields':crm_fields, 'state':[('end', 'Cancel'),('choose', 'Choose')]}
        },
        'choose': {
            'actions': [],
            'result': {'type': 'action', 'action':_open_window_selected_partners, 'state':'end'}
        }

    }
show_partners("show_partners")
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

