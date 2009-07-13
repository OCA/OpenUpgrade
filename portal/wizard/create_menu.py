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

first_form = '''<?xml version="1.0"?>
<form string="Create menu : ">
    <separator string="The new menu will be available for the portal :" colspan="4"/>
    <field name="portal_id"/>
        <separator string="The new menu will open this model :" colspan="4"/>
    <field name="model_id"/>
</form>'''
first_fields = {
    'portal_id': {'string':'Portal', 'type':'many2one', 'required':True, 'relation': 'portal.portal'},
    'model_id': {'string':'Model', 'type':'many2one', 'required':True, 'relation': 'portal.model'},
}

second_form = '''<?xml version="1.0"?>
<form string="Create menu : ">
    <separator string="Name of the new menu :" colspan="4"/>
    <field name="menu"/>
    <separator string="The new menu is located under:" colspan="4"/>
    <field name="parent_menu_id"/>
    <separator string="Action triggered by the new menu :" colspan="4"/>
    <field name="action_id"/>
    <separator string="Views used to display the action :" colspan="4"/>
    <field name="view_id_tree" colspan="4"/>
    <field name="view_id_form" colspan="4"/>
    <field name="view_type" colspan="4"/>
</form>'''
second_fields = {
    'menu': {'string':'Name', 'type':'char', 'required':True, 'size':64},
    'action_id': {'string':'Action', 'type':'many2one', 'required':True,
                  'relation': 'ir.actions.act_window',},
    'parent_menu_id': {'string':'Parent Menu', 'type':'many2one', 'required':True,
                  'relation': 'ir.ui.menu',},
    'view_id_tree': {'string':'Tree View', 'type':'many2one', 'required':False,
                  'relation': 'ir.ui.view',},
    'view_id_form': {'string':'Form View', 'type':'many2one', 'required':False,
                  'relation': 'ir.ui.view',},
    'view_type' :{'string': 'Use Form View By Default', 'type': 'boolean', 'required':False},
}

def _create_menu(self, cr, uid, data, context):
    """
    Create the new menuitem and open a new tab with the result.
    """
    portal_obj=pooler.get_pool(cr.dbname).get('portal.portal')
    action_menu_id= portal_obj.create_menu(cr, uid,
        data['form']['portal_id'],
        data['form']['model_id'],
        data['form']['menu'],
        data['form']['action_id'],
        data['form']['parent_menu_id'],
        {'form':data['form']['view_id_form'],'tree':data['form']['view_id_tree']},
        data['form']['view_type'],
        context)
    action=  pooler.get_pool(cr.dbname).get('ir.actions.act_window').read(cr,uid,[action_menu_id])
    return action[0] #FIXME : does not work anymore [bch20070612]

def _add_domain(self, cr, uid, data, context):
    """
    Add a domain to the model field of the second windows of the wizard.
    """
    model= pooler.get_pool(cr.dbname).get('portal.model').browse(cr,uid,data['form']['model_id'])
    portal= pooler.get_pool(cr.dbname).get('portal.portal').browse(cr,uid,data['form']['portal_id'])
    second_fields['action_id']['domain']= [('res_model','=',model.model_id.model)]
    second_fields['parent_menu_id']['domain']= [('parent_id','child_of',[portal.menu_id.id])]
    second_fields['view_id_tree']['domain']= [('model','=',model.model_id.model)]
    second_fields['view_id_form']['domain']= [('model','=',model.model_id.model)]
    return {}


class wizard_report(wizard.interface):
    states = {
        'init': {
            'actions': [], 
            'result': {'type':'form',
                       'arch':first_form,
                       'fields':first_fields,
                       'state':[('end','_Cancel'),('second','_Next')]}
        },  
        'second': {
            'actions': [_add_domain], 
            'result': {'type':'form',
                       'arch':second_form,
                       'fields':second_fields,
                       'state':[('end','_Cancel'),('init','_Back'),('create','_Next')]}
        },
        'create': {
            'actions': [], 
            'result': {'type':'action',
                       'action':_create_menu,
                       'state':'end'}
        },      
}
wizard_report('portal.create_menu')


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

