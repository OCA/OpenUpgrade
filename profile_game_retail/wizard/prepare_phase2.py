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
        sm_action=['menu_purchase_order_draft','menu_action_invoice_tree8']
        lm_action=['mrp_Sched_all','menu_action_picking_tree4','menu_action_picking_tree']
        fm_action=['menu_action_invoice_tree9','menu_invoice_draft','menu_action_invoice_tree7']

        pool=pooler.get_pool(cr.dbname)
        mod_obj = pooler.get_pool(cr.dbname).get('ir.model.data')
        phase1_obj=pool.get('profile.game.retail.phase1')

        obj=phase1_obj.browse(cr,uid,data['id'])
        phase1_obj.write(cr,uid,data['id'],{'state':'started_phase2'})

        user_ids=pool.get('res.users').search(cr,uid,[])
        user_browse=pool.get('res.users').browse(cr,uid,user_ids)
        sc_ids=pool.get('ir.ui.view_sc').search(cr,uid,[('user_id','in',user_ids)])
        pool.get('ir.ui.view_sc').unlink(cr,uid,sc_ids)

        result = mod_obj._get_id(cr, uid, 'profile_game_retail', 'open_board_game2')
        id = mod_obj.read(cr, uid, [result], ['res_id'])[0]['res_id']
        for user in user_ids:
            pool.get('res.users').write(cr,uid,user,{'action_id':id})

        for user in user_browse:
            if user.login=='sale':
                for action in sm_action:
                    val={}
                    if action =='menu_purchase_order_draft':
                        module='purchase'
                    else:
                        module='account'
                    res=mod_obj._get_id(cr, uid, module, action)
                    res_id = mod_obj.read(cr, uid, [res], ['res_id'])[0]['res_id']
                    val['res_id']=res_id
                    val['resource']='ir.ui.menu'
                    val['user_id'] =user.id
                    val['name']=pool.get('ir.ui.menu').read(cr,uid,[res_id],['name'])[0]['name']
                    pool.get('ir.ui.view_sc').create(cr,uid,val)

            if user.login=='logistic':
                for action in lm_action:
                    val={}
                    if action =='mrp_Sched_all':
                        module='mrp'
                    else:
                        module='stock'
                    res=mod_obj._get_id(cr, uid, module, action)
                    res_id = mod_obj.read(cr, uid, [res], ['res_id'])[0]['res_id']
                    val['res_id']=res_id
                    val['resource']='ir.ui.menu'
                    val['user_id'] =user.id
                    val['name']=pool.get('ir.ui.menu').read(cr,uid,[res_id],['name'])[0]['name']
                    pool.get('ir.ui.view_sc').create(cr,uid,val)

            if user.login=='finance':
                for action in fm_action:
                    val={}
                    res=mod_obj._get_id(cr, uid, 'account', action)
                    res_id = mod_obj.read(cr, uid, [res], ['res_id'])[0]['res_id']
                    val['res_id']=res_id
                    val['resource']='ir.ui.menu'
                    val['user_id'] =user.id
                    val['name']=pool.get('ir.ui.menu').read(cr,uid,[res_id],['name'])[0]['name']
                    pool.get('ir.ui.view_sc').create(cr,uid,val)

       # if obj.state != 'done':
           # phase1_obj.write(cr,uid,data['id'],{'state':'done'})
        return  {
        'name': 'Business Game',
        'view_type': 'form',
        'res_model': 'profile.game.retail.phase2',
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