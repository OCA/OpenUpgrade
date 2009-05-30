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
import netsvc

    
def selection_list(self, cr, uid, context):
    temp = pooler.get_pool(cr.dbname).get('dm.workitem').SELECTION_LIST 
    return temp

parameter_form = '''<?xml version="1.0"?>
<form string="Modify Workitem" colspan="4">
    <field name="state" colspan="4"/>
    <field name="action_time" colspan="4"/>
</form>'''

parameter_fields = {
    'action_time' : {'string':'Action Time', 'type':'datetime','required':True},
    'state' : {'string':'Status', 'type':'selection', 'selection':selection_list,'required':True},
}

def _change_state_action_time(self, cr, uid, data, context):
    print "---------------------", data
    workitem_obj = pooler.get_pool(cr.dbname).get('dm.workitem')
    workitem_obj.write(cr, uid, data['ids'], {'state': data['form']['state'],'action_time':data['form']['action_time']})
    return {}

class wizard_workitem(wizard.interface):
    states = {
        'init': {
            'actions': [],
            'result': {'type': 'form', 'arch':parameter_form, 'fields': parameter_fields, 'state':[('end','Cancel'),('done', 'Modify')]}

        },
        'done': {
            'actions': [],
            'result': {
                'type': 'action',
                'action': _change_state_action_time,
                'state': 'end'
            }
        },
    }
wizard_workitem("wizard.workitem")