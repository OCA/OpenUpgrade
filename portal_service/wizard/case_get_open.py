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

def _case_get_open(self, cr, uid, data, context):
    obj = pooler.get_pool(cr.dbname).get('crm.case')

    obj.case_open(cr, uid, data['ids'])

#   cr.execute("select id from ir_ui_view where name like 'Detailed Lead Tree' limit 1")
#   res_tree = cr.fetchone()
#   cr.execute("select id from ir_ui_view where name like 'Detailed Lead Form' limit 1")
#   res_form = cr.fetchone()
#
#   vids = []
#   vids.append((0,0, {
#       'view_id': res_form[0],
#       'view_mode': 'form',
#   }))
#   vids.append((0,0, {
#       'sequence':1,
#       'view_id': res_tree[0],
#       'view_mode': 'tree',
#   }))

    action= {
        'name': 'Detailed Lead',
        'view_type': 'form',
        'view_mode': 'form,tree',
        'res_model': 'crm.case',
        'type': 'ir.actions.act_window',
#       'view_ids': vids,
        'res_id': data['id']            
        }
#   print action

    return action

class case_get_open(wizard.interface):
    states = {
        'init': {
            'actions': [],
            'result': {'type': 'action', 'action': _case_get_open, 'state':'end'}
        }
    }

case_get_open('case_get_open')
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

