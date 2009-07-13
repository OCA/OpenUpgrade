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

from osv import fields, osv
import pooler

class portal_portal(osv.osv):
    _name = "portal.portal"
    _description = "Portal"
    _columns = {
        'name': fields.char('Portal Name',size=64,required=True),
        'group_id': fields.many2one('res.groups', 'Associated Group',required=True),
        'menu_id': fields.many2one('ir.ui.menu','Main Menu', required=True),
        'menu_action_id': fields.many2one('ir.actions.act_window', 'User Menu Action', readonly=True,
            help='''Default main menu for the users of the portal. This field is auto-completed at creation. '''),
        'home_action_id': fields.many2one('ir.actions.act_window', 'User Home Action', help='Complete this field to provide a Home menu different from the Main menu.'),
        'company_id': fields.many2one('res.company', 'Company', required=True),
        }

    def create_action_menu(self,cr,uid,action_id,action_name,context):
        """
        Create default menu for the users of the portal.
        """
        mod_obj = self.pool.get('ir.model.data')
        result = mod_obj._get_id(cr, uid, 'base', 'view_menu')
        menu_action_id = self.pool.get('ir.actions.act_window').create(cr,uid, {
            'name': action_name+ ' main menu',
            'usage': 'menu',
            'type':'ir.actions.act_window',
            'res_model': "ir.ui.menu",
            'domain': "[('parent_id','=',"+str(action_id)+")]",
            'view_type': 'tree',
            'view_id': mod_obj.read(cr, uid, [result], ['res_id'])[0]['res_id']
            })
        return menu_action_id


    def create(self, cr, user, vals, context={}):
        if not vals.get('menu_action_id') :
            vals['menu_action_id']= self.create_action_menu(cr,user,vals['menu_id'], vals['name'],context)
        return super(portal_portal, self).create(cr, user, vals, context)

    def create_menu(self, cr, uid,portal_id, portal_model_id, menu_name, action_id,parent_menu_id=None,view_ids=None,view_type=False,context=None):
        """
        Create a menuitem for the given portal and model with the given name and action.
        """

        assert portal_id and portal_model_id and menu_name and action_id, "Create_menu does not accept null values"

        v=[]
        if view_type:
            v.append('form')
            v.append('tree')
        else:
            v.append('tree')
            v.append('form')

        portal= self.pool.get('portal.portal').browse(cr,uid,portal_id)
        model= self.pool.get('portal.model').browse(cr,uid,portal_model_id)
        action_obj= self.pool.get('ir.actions.act_window')
        action= action_obj.browse(cr,uid,action_id)
        ## Create the menu:
        menu_id=self.pool.get('ir.ui.menu').create(cr, uid, {
            'name': menu_name,
            'parent_id': parent_menu_id or portal.menu_id.id,
            'icon': 'STOCK_NEW'
            })

        available_view={}
        for view in model.view_ids:
            available_view[view.type]= view.id
        vids = []
        i = 0
        ## Fetch the views:
        for view in action_obj.browse(cr,uid,action_id,context=context).views:
            vids.append((0,0, {
                'sequence':i,
                'view_id': available_view.get(view[1], view[0]),
                'view_mode': view[1],
            }))
            i+=1

        (unused1, unused2, cur_first_view) = vids[0]

        if view_ids['form'] != False:
            if view_ids['tree'] != False:
                vids[0]=(0,0, {
                'sequence':0,
                'view_id': view_ids[v[0]],
                'view_mode': v[0],
                })
                vids[1]=(0,0, {
                'sequence':1,
                'view_id': view_ids[v[1]],
                'view_mode': v[1],
                })
            else:
                if view_type & (cur_first_view['view_mode']=='tree'):
                    temp=vids[0]
                    vids[0]=vids[1]
                    vids[1]=temp
                if v[0] =='form':
                    vids[0]=(0,0, {
                    'sequence':0,
                    'view_id': view_ids['form'],
                    'view_mode': 'form',
                    })
                else:
                    vids[1]=(0,0, {
                    'sequence':1,
                    'view_id': view_ids['form'],
                    'view_mode': 'form',
                    })
        else:
            if view_ids['tree'] != False:
                if view_type & (cur_first_view['view_mode']=='tree'):
                    temp=vids[0]
                    vids[0]=vids[1]
                    vids[1]=temp
                if v[0] =='tree':
                    vids[0]=(0,0, {
                    'sequence':0,
                    'view_id': view_ids['tree'],
                    'view_mode': 'tree',
                    })
                else:
                    vids[1]=(0,0, {
                    'sequence':1,
                    'view_id': view_ids['tree'],
                    'view_mode': 'tree',
                    })
            else:
                if view_type & (cur_first_view['view_mode']=='tree'):
                    temp=vids[0]
                    vids[0]=vids[1]
                    vids[1]=temp

        ## Duplicate the action and give the fetched views to the new one:
        action_id = action_obj.copy(cr,uid, action.id,{
            'name': menu_name,
            'view_ids': vids,
            'view_type': v[0]
            },context=context)

        ## Create the values:
        value_id = self.pool.get('ir.values').create(cr, uid, {
            'name': 'AutoGenerated by portal module',
            'key2': 'tree_but_open',
            'model': 'ir.ui.menu',
            'res_id': menu_id,
            'value': 'ir.actions.act_window,%d'%action_id,
            'object': True
            })
        ## add the rule_group to the user
        if model.rule_group_id:
            group_obj = self.pool.get('res.groups')
            group_obj.write(cr,uid,[portal.group_id.id],{'rule_groups': [(4,model.rule_group_id.id)]})
        return action_id

portal_portal()


class portal_model(osv.osv):
    _name = "portal.model"
    _description = "Portal Model"
    _columns = {
        'name': fields.char('Name',size=64,),
        'model_id': fields.many2one('ir.model','Model',required=True),
        'view_ids': fields.many2many('ir.ui.view','portal_model_view_rel','model_id','view_id','Views'),
        'rule_group_id': fields.many2one('ir.rule.group','Rule group'),
        }
portal_model()

class ir_actions_act_report_xml(osv.osv):
    _inherit="ir.actions.report.xml"
    _columns={
        "portal_visible": fields.boolean('Visible in Portal')
        }
    _defaults = {
        'portal_visible': lambda *a: True,
    }
ir_actions_act_report_xml()

class ir_actions_act_report_custom(osv.osv):
    _inherit="ir.actions.report.custom"
    _columns={
        "portal_visible": fields.boolean('Visible in Portal')
        }
    _defaults = {
        'portal_visible': lambda *a: True,
    }
ir_actions_act_report_custom()

class ir_actions_act_wizard(osv.osv):
    _inherit="ir.actions.wizard"
    _columns={
        "portal_visible": fields.boolean('Visible in Portal')
        }
    _defaults = {
        'portal_visible': lambda *a: True,
    }
ir_actions_act_wizard()

class ir_actions_act_window(osv.osv):
    _inherit="ir.actions.act_window"
    _columns={
        "portal_visible": fields.boolean('Visible in Portal')
        }
    _defaults = {
        'portal_visible': lambda *a: True,
    }
ir_actions_act_window()

class portal_config_install_modules_wizard(osv.osv_memory):
    _name='portal.config.install_modules_wizard'
    _columns = {
        'portal_sale':fields.boolean('Portal for Sale Module'),
        'portal_service':fields.boolean('Portal for Service Module'),
        'portal_account':fields.boolean('Portal for Account Module'),
        'portal_analytic':fields.boolean('Portal for Analytic Account Module'),
    }
    def action_cancel(self,cr,uid,ids,conect=None):
        return {
                'view_type': 'form',
                "view_mode": 'form',
                'res_model': 'ir.actions.configuration.wizard',
                'type': 'ir.actions.act_window',
                'target':'new',
         }
    def action_install(self, cr, uid, ids, context=None):
        result=self.read(cr,uid,ids)
        mod_obj = self.pool.get('ir.module.module')
        for res in result:
            for r in res:
                if r<>'id' and res[r]:
                    ids = mod_obj.search(cr, uid, [('name', '=', r)])
                    mod_obj.button_install(cr, uid, ids, context=context)
        cr.commit()
        db, pool = pooler.restart_pool(cr.dbname,update_module=True)
        return {
                'view_type': 'form',
                "view_mode": 'form',
                'res_model': 'ir.actions.configuration.wizard',
                'type': 'ir.actions.act_window',
                'target':'new',
            }
portal_config_install_modules_wizard()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

