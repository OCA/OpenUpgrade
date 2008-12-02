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

def get_ready_phase2(self, cr, uid, data, context):
        pool = pooler.get_pool(cr.dbname)
        sm_group = ['Purchase / Manager','Purchase / User','Employee','Finance / Accountant','Finance / Invoice']
        sm_group_ids = pool.get('res.groups').search(cr,uid,[('name','in',sm_group)])
        sm_roles = ['Purchase','Invoice']
        sm_role_ids = pool.get('res.roles').search(cr,uid,[('name','in',sm_roles)])
        mod_obj = pooler.get_pool(cr.dbname).get('ir.model.data')
        phase1_obj = pool.get('profile.game.retail.phase1')
        obj = phase1_obj.browse(cr,uid,data['id'])

        user_ids=pool.get('res.users').search(cr,uid,[])
        user_browse=pool.get('res.users').browse(cr,uid,user_ids)

        result = mod_obj._get_id(cr, uid, 'profile_game_retail', 'open_board_game2')
        id = mod_obj.read(cr, uid, [result], ['res_id'])[0]['res_id']
        for user in user_ids:
            pool.get('res.users').write(cr,uid,user,{'action_id':id})

        sale_user=pool.get('res.users').search(cr,uid,[('login','=','sale')])
        cr.execute('delete from res_groups_users_rel where uid =%d'%(sale_user[0]))
        cr.execute('delete from res_roles_users_rel where uid =%d'%(sale_user[0]))
        pool.get('res.users').write(cr,uid,sale_user[0],{'groups_id':[[6,0,sm_group_ids]],
                                                    'roles_id':[[6,0,sm_role_ids]]})
      #  phase1_obj.write(cr,uid,data['id'],{'state':'started_phase2'})
        return  {
        'name': 'Business Game',
        'view_type': 'form',
        'res_model': 'profile.game.retail',
        'view_id':False,
        'type': 'ir.actions.act_window',
        }

class prepare_phase2(wizard.interface):
     states = {
        'init': {
            'actions': [],
            'result': {'type': 'action', 'action' : get_ready_phase2, 'state' : 'end'}
        },
    }

prepare_phase2('game.prepare.phase2')
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: