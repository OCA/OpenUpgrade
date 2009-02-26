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
import netsvc

def _after_login(self, cr, uid, data, context):
    user_pool = pooler.get_pool(cr.dbname).get('res.users')
    action_pool = pooler.get_pool(cr.dbname).get('personal.base.action.login')
    wizard_pool = pooler.get_pool(cr.dbname).get('ir.actions.wizard')
    for id in action_pool.search(cr, uid, []):
        action = action_pool.browse(cr, uid, id)
        if action.action_id.type == 'ir.actions.wizard':
            my_wizard = wizard_pool.browse(cr, uid, action.action_id.id)
            service = netsvc.LocalService('wizard.' + my_wizard.wiz_name)
            service.execute(cr.dbname, uid, {"form":{}})
    
    res = user_pool.search(cr, uid, [])
    user = user_pool.browse(cr, uid, res[0])
    if user.first_login:
        user_pool.write(cr, uid, uid, {'first_login': False})
            
    return {}

class wizard_after_login(wizard.interface):
    states = {
        'init' : {
            'actions' : [],
            'result': {'type': 'action', 'action':_after_login, 'state':'end'}
        },
    }
wizard_after_login("personal.base.wizard.after_login")
