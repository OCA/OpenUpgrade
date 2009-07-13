# -*- encoding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2007-2008 Sandas. (http://www.sandas.eu) All Rights Reserved.
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
############################################################

import wizard
import pooler

class wiz_open_line_entry(wizard.interface):
    def _open_line_entry(self, cr, uid, data, context):
        pool = pooler.get_pool(cr.dbname)
        lines = pool.get('personal.base.account.entry.line').browse(cr, uid, data['ids'])
        ids = []
        model = None
        for l in lines:
            if not model:
                model = l.parent_id.created_in_model_id
            if model.id == l.parent_id.created_in_model_id.id:
                ids.append(l.parent_id.id)
        if ids != []:
            if model.model == 'personal.base.account.entry':
                id_field_name = 'id'
            else:
                id_field_name = 'entry_id'
                
            domain = "[('" + id_field_name + "','in', [" + ','.join(map(str,ids)) + "])"
            if model.model == 'personal.base.account.entry':
                domain = domain + ",('created_in_model_id', '=', %d)" % model.id
            domain = domain + ']'
            return {
                    'domain': domain,
                    #'name': 'Entries',
                    'view_type': 'form',
                    'view_mode': 'tree,form',
                    'res_model': model.model,
                    'view_id': False,
                    'type': 'ir.actions.act_window'
            }
            
        return {}
    states = {
        'init': {
            'actions': [],
            'result': {'type':'action', 'action':_open_line_entry, 'state':'end'}
        }
    }
wiz_open_line_entry('personal.base.account.open_line_entry')
