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
import datetime

form='''<?xml version="1.0"?>
<form string="Choose the timespan for the report">
    <field name="date_from" colspan="1" />
    <field name="date_to" colspan="1" />
    <field name="depts" colspan="4" />
</form>'''

back_form='''<?xml version="1.0"?>
<form string="Notification">
<label string="You should select less than 90 days for the proper layout of report. Try again." colspan="4"/>
</form>'''

back_fields={
}
class wizard_report(wizard.interface):
    def _check(self, cr, uid, data, context):
        cr.execute("select CURRENT_DATE")
        _date_from=cr.fetchone()
        cr.execute("select CURRENT_DATE + 89")
        _date_to=cr.fetchone()

        data['form']['date_from']=_date_from[0]
        data['form']['date_to']=_date_to[0]

        return data['form']
    def _check90days(self,cr,uid,data,context):

        first_date=data['form']['date_from']
        last_date=data['form']['date_to']

        som = datetime.date(int(first_date[0:4]),int(first_date[5:7]),int(first_date[8:10]))
        eom = datetime.date(int(last_date[0:4]),int(last_date[5:7]),int(last_date[8:10]))

        day_diff=eom-som
        if day_diff.days>90:
           return 'notify'
        else:
           return 'report'

    fields={
        'date_from':{
            'string':'From',
            'type':'date',
            'required':True,

        },
        'date_to':{
            'string':'To',
            'type':'date',
            'required':True,

        },
        'depts': {'string': 'Department(s)', 'type': 'many2many', 'relation': 'hr.department','required': True},

    }

    states={
        'init':{
            'actions':[_check],
            'result':{'type':'form', 'arch':form, 'fields':fields, 'state':[('end', 'Cancel'), ('state_next', 'Print')]}
        },
        'state_next':{
            'actions':[],
            'result': {'type':'choice','next_state':_check90days}
        },
        'notify': {
            'actions': [],
            'result': {'type':'form','arch':back_form,'fields':back_fields,'state':[('end','Ok')]}
        },
        'report':{
            'actions':[],
            'result':{'type':'print', 'report':'holidays.summary', 'state':'end'}
        }
    }
wizard_report('hr.holidays.summary')
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

