# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>). All Rights Reserved
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
import datetime
import mx.DateTime
from mx.DateTime import RelativeDateTime, now, DateTime, localtime
import time
import math

def assign_full_access_rights(self, cr, uid, data, context):
    pool = pooler.get_pool(cr.dbname)
    gp = pool.get('res.groups')
    user_obj = pool.get('res.users')
    user_name = ['sale','logistic','hr','finance']
    user_ids = user_obj.search(cr, uid, [('login','in',user_name)])
    gp_ids = gp.search(cr, uid, [('users','in',user_ids)])
    gp_name = ['Game / Phase 2 / Sales Manager','Game / Phase 2 / HR Manager','Game / Phase 2 / Logistic Manager','Game / Phase 2 / Finance Manager']
    for name in gp_name:
        new_id = gp.create(cr, uid, {'name':name})
        for group in gp.browse(cr, uid, gp_ids):
            for access in group.model_access:
                pool.get('ir.model.access').create(cr, uid,{'name' : access.name,
                                             'model_id' : access.model_id.id,
                                             'group_id' : access.group_id,
                                             'group_id' : new_id,
                                             'perm_read' : True,
                                             'perm_write' : True,
                                             'perm_create' : True,
                                             'perm_unlink' : True })
        if name == 'Game / Phase 2 / Sales Manager':
            login = 'sale'
        elif name == 'Game / Phase 2 / HR Manager':
            login = 'hr'
        elif name == 'Game / Phase 2 / Logistic Manager':
            login = 'logistic'
        else:
            login = 'finance'
        user = user_obj.search(cr, uid, [('login','=',login)])
        user_browse = user_obj.browse(cr, uid, user)[0]
        add_menu = []
        for user_gp in user_browse.groups_id:
            for menu_id in user_gp.menu_access:
                add_menu.append(menu_id.id)

        cr.execute('delete from res_groups_users_rel where uid =%d'%(user[0]))
        cr.execute('delete from res_roles_users_rel where uid =%d'%(user[0]))
        gp.write(cr, uid, new_id,{'menu_access' : [[6,0,add_menu]],'users':[[6,0,user]]})
    role_ids = pool.get('res.roles').search(cr, uid, [])
    for user in user_ids:
        user_obj.write(cr, uid, user, {'roles_id':[[6,0,role_ids]]})
    return


def create_phase2_menu(self, cr, uid, data, context):
    pool = pooler.get_pool(cr.dbname)
    mod_obj = pool.get('ir.model.data')
    result = mod_obj._get_id(cr, uid, 'profile_business_game', 'business_game')
    parent_id = mod_obj.read(cr, uid, [result], ['res_id'])[0]['res_id']
    result = mod_obj._get_id(cr, uid, 'profile_business_game', 'action_game_detail_form')
    action_id = mod_obj.read(cr, uid, [result], ['res_id'])[0]['res_id']
    menu_id = pool.get('ir.ui.menu').create(cr, uid, {
            'name': 'Business Game Details',
            'parent_id': parent_id,
            'icon': 'STOCK_NEW'
            })
    value_id = pool.get('ir.values').create(cr, uid, {
            'name': 'Business Game Phase2',
            'key2': 'tree_but_open',
            'model': 'ir.ui.menu',
            'res_id': menu_id,
            'value': 'ir.actions.act_window,%d'%action_id,
            'object': True
            })
    return

def create_budgets(self, cr, uid, data, context={}):
    pool = pooler.get_pool(cr.dbname)
    for code in ('HR','EXP','SAL'):
        if code == 'HR':
            name = code
            domain = [('code','in',['631100','641100','691000'])]
        elif code == 'EXP':
            name = 'Expenses'
            domain = [('code','ilike','6%'),('code','not in',['631100','641100','691000'])]
        else:
            name = 'Sales'
            domain = [('code','ilike','7%')]
        acc_ids = pool.get('account.account').search(cr, uid, domain)
        pool.get('account.budget.post').create(cr, uid, {'name':name,'code':code,'account_ids':[[6,0,acc_ids]]})
    return

def get_ready_phase2(self, cr, uid, data, context):
        if uid != 1:
            raise wizard.except_wizard('Permission Denied','Only Admin can start the Phase2')
        create_phase2_menu(self, cr, uid, data, context)
        assign_full_access_rights(self, cr, uid, data, context)
        create_budgets(self,cr, uid, data, context)
        pool = pooler.get_pool(cr.dbname)
        phase2_obj = pool.get('profile.game.phase2')
        phase2_obj.create_sale_periods(cr, uid, data, context)
        phase2_obj.create_sale_forecast_stock_planning_data(cr, uid, data, time.strftime('%Y'), context)

        lm_action = ['menu_stock_planning','menu_action_orderpoint_form']
        mod_obj = pool.get('ir.model.data')
        phase1_obj = pool.get('profile.game.phase1')
        obj = phase1_obj.browse(cr, uid, data['id'])

        user_ids = pool.get('res.users').search(cr, uid, [])
        user_browse = pool.get('res.users').browse(cr, uid, user_ids)

        sc_ids = pool.get('ir.ui.view_sc').search(cr, uid, [('user_id','in',user_ids)])
        pool.get('ir.ui.view_sc').unlink(cr, uid, sc_ids)

        result = mod_obj._get_id(cr, uid, 'profile_business_game', 'open_board_game2')
        id = mod_obj.read(cr, uid, [result], ['res_id'])[0]['res_id']
        for user in user_ids:
            pool.get('res.users').write(cr, uid, user, {'action_id':id})

        for user in user_browse:
            if user.login in ('sale','finance'):
                val = {}
                if user.login=='sale':
                    res=mod_obj._get_id(cr, uid, 'sale_forecast', 'menu_sale_forecast_my_managing')

                if user.login=='finance':
                    res=mod_obj._get_id(cr, uid, 'account_budget', 'menu_budget_post_form')

                res_id = mod_obj.read(cr, uid, [res], ['res_id'])[0]['res_id']
                val['res_id']=res_id
                val['resource']='ir.ui.menu'
                val['user_id'] =user.id
                val['name']=pool.get('ir.ui.menu').read(cr,uid,[res_id],['name'])[0]['name']
                pool.get('ir.ui.view_sc').create(cr,uid,val)

            if user.login=='logistic':
                for action in lm_action:
                    val={}
                    if action =='menu_action_orderpoint_form':
                        module='mrp'
                    else:
                        module='stock_planning'
                    res=mod_obj._get_id(cr, uid, module, action)
                    res_id = mod_obj.read(cr, uid, [res], ['res_id'])[0]['res_id']
                    val['res_id']=res_id
                    val['resource']='ir.ui.menu'
                    val['user_id'] =user.id
                    val['name']=pool.get('ir.ui.menu').read(cr,uid,[res_id],['name'])[0]['name']
                    pool.get('ir.ui.view_sc').create(cr,uid,val)
        phase1_obj.write(cr,uid,data['id'],{'state':'started_phase2'})
        return  {
        'name': 'Business Game',
        'view_type': 'form',
        'res_model': 'profile.game.phase2',
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