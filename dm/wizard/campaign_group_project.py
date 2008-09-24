# -*- encoding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2005-2006 TINY SPRL. (http://tiny.be) All Rights Reserved.
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsability of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# garantees and support are strongly adviced to contract a Free Software
# Service Company
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
##############################################################################

#
# Order Point Method:
#    - Order if the virtual stock of today is bellow the min of the defined order point
#

import wizard
import pooler

parameter_form = '''<?xml version="1.0"?>
<form string="Campaign Group" colspan="4">
    <field name="project_id"
/>
</form>'''

parameter_fields = {
    'project_id': {'string':'Project', 'type':'many2one', 'required':True, 'relation':'project.project', 'domain': [('active','<>',False)]},
}

def _create_duplicate(self, cr, uid, data, context):
    print context,"---------------------------------------------------------------------"
    campaign_group_obj=pooler.get_pool(cr.dbname).get('dm.campaign.group')
    project_obj = pooler.get_pool(cr.dbname).get('project.project')
    duplicate_project_id= project_obj.copy(cr, uid,data['form']['project_id'], {'active': True})
    campaign = campaign_group_obj.browse(cr, uid, data['id'])
    project_obj.write(cr, uid, duplicate_project_id, {'name': project_obj.browse(cr, uid, duplicate_project_id, context).name + " for " + campaign.name})
    campaign_group_obj.write(cr, uid, [data['id']], {'project_id': duplicate_project_id})
    return {}

class wizard_campaign_group_project(wizard.interface):
    states = {
        'init': {
            'actions': [],
            'result': {'type': 'form', 'arch':parameter_form, 'fields': parameter_fields, 'state':[('end','Cancel'),('done', 'Ok')]}

        },
        'done':{
                'actions':[_create_duplicate],
                'result' : {'type':'state', 'state':'end'}
                }
    }
wizard_campaign_group_project('campaign.group.project')

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
