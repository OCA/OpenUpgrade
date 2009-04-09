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

def _campaign_group_tasks(self, cr, uid, data, context):
    campaign_group_id = data['id']
    cr.execute('''SELECT project_id FROM dm_campaign_group WHERE id = %d '''% (campaign_group_id, ))
    res = cr.fetchone()
    if not res[0]:
        raise wizard.except_wizard('Error !', 'No project defined for this campaign. You can create one with the retro-planning button !')
    value = {
        'domain': [('project_id', '=', res[0])],
        'name': 'Tasks',
        'view_type': 'form',
        'view_mode': 'tree,form,calendar',
        'res_model': 'project.task',
        'context': { },
        'type': 'ir.actions.act_window'
    }
    return value

class wizard_campaign_group_tasks(wizard.interface):
    states = {
        'init': {
            'actions': [],
            'result': {
                'type': 'action',
                'action': _campaign_group_tasks,
                'state': 'end'
            }
        },
    }
wizard_campaign_group_tasks("wizard_campaign_group_tasks")
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

