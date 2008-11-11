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


import time
import wizard
import osv
import pooler

base_url_menu_form = '''<?xml version="1.0"?>
<form string="Create URL Menus">
    <field name="url_menu_name"/>
    <field name="url_menu_parent_id"/>
    <field name="target_id"/>
</form>'''

base_url_menu_fields = {
    'url_menu_name': {'string':'URL Menu Name', 'type':'char', 'required':True, 'size':64},
    'url_menu_parent_id': {'string':'Parent Menu', 'type':'many2one', 'relation':'ir.ui.menu', 'required':False},
    'target_id': {'string':'Target URL', 'type':'char', 'required':False, 'size':128},
}

def base_url_menu_create(self, cr, uid, data, context):
    pool = pooler.get_pool(cr.dbname)

    action_id = pool.get('ir.actions.url').create(cr,uid, {
        'name': data['form']['url_menu_name']+' Url',
        'type': 'ir.actions.act_url',
        'url': data['form']['target_id'],
        'target': 'new'
    })
    menu_id=pool.get('ir.ui.menu').create(cr, uid, {
        'name': data['form']['url_menu_name'],
        'parent_id': data['form']['url_menu_parent_id'],
        'icon': 'STOCK_JUSTIFY_FILL',
    })

    pool.get('ir.values').create(cr, uid, {
        'name': 'Open url',
        'key': 'action',
        'key2': 'tree_but_open',
        'model': 'ir.ui.menu',
        'res_id': menu_id,
        'value': 'ir.actions.url,%d'%action_id,
        'object': True
    })
    return {}

class wizard_url_menu_create(wizard.interface):
    states = {
        'init': {
            'actions': [], 
            'result': {'type':'form', 'arch':base_url_menu_form, 'fields':base_url_menu_fields, 'state':[('end','Cancel'),('create','Create menu Entries')]}
        },
        'create': {
            'actions': [base_url_menu_create],
            'result': {'type':'state', 'state':'end'}
        }
    }
wizard_url_menu_create('url.menu.menu')
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

