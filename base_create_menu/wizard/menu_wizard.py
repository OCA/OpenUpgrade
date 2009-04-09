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
import osv
import pooler


icons = map(lambda x: (x,x), ['STOCK_ABOUT', 'STOCK_ADD', 'STOCK_APPLY', 'STOCK_BOLD',
'STOCK_CANCEL', 'STOCK_CDROM', 'STOCK_CLEAR', 'STOCK_CLOSE', 'STOCK_COLOR_PICKER',
'STOCK_CONNECT', 'STOCK_CONVERT', 'STOCK_COPY', 'STOCK_CUT', 'STOCK_DELETE',
'STOCK_DIALOG_AUTHENTICATION', 'STOCK_DIALOG_ERROR', 'STOCK_DIALOG_INFO',
'STOCK_DIALOG_QUESTION', 'STOCK_DIALOG_WARNING', 'STOCK_DIRECTORY', 'STOCK_DISCONNECT',
'STOCK_DND', 'STOCK_DND_MULTIPLE', 'STOCK_EDIT', 'STOCK_EXECUTE', 'STOCK_FILE',
'STOCK_FIND', 'STOCK_FIND_AND_REPLACE', 'STOCK_FLOPPY', 'STOCK_GOTO_BOTTOM',
'STOCK_GOTO_FIRST', 'STOCK_GOTO_LAST', 'STOCK_GOTO_TOP', 'STOCK_GO_BACK',
'STOCK_GO_DOWN', 'STOCK_GO_FORWARD', 'STOCK_GO_UP', 'STOCK_HARDDISK',
'STOCK_HELP', 'STOCK_HOME', 'STOCK_INDENT', 'STOCK_INDEX', 'STOCK_ITALIC',
'STOCK_JUMP_TO', 'STOCK_JUSTIFY_CENTER', 'STOCK_JUSTIFY_FILL',
'STOCK_JUSTIFY_LEFT', 'STOCK_JUSTIFY_RIGHT', 'STOCK_MEDIA_FORWARD',
'STOCK_MEDIA_NEXT', 'STOCK_MEDIA_PAUSE', 'STOCK_MEDIA_PLAY',
'STOCK_MEDIA_PREVIOUS', 'STOCK_MEDIA_RECORD', 'STOCK_MEDIA_REWIND',
'STOCK_MEDIA_STOP', 'STOCK_MISSING_IMAGE', 'STOCK_NETWORK', 'STOCK_NEW',
'STOCK_NO', 'STOCK_OK', 'STOCK_OPEN', 'STOCK_PASTE', 'STOCK_PREFERENCES',
'STOCK_PRINT', 'STOCK_PRINT_PREVIEW', 'STOCK_PROPERTIES', 'STOCK_QUIT',
'STOCK_REDO', 'STOCK_REFRESH', 'STOCK_REMOVE', 'STOCK_REVERT_TO_SAVED',
'STOCK_SAVE', 'STOCK_SAVE_AS', 'STOCK_SELECT_COLOR', 'STOCK_SELECT_FONT',
'STOCK_SORT_ASCENDING', 'STOCK_SORT_DESCENDING', 'STOCK_SPELL_CHECK',
'STOCK_STOP', 'STOCK_STRIKETHROUGH', 'STOCK_UNDELETE', 'STOCK_UNDERLINE',
'STOCK_UNDO', 'STOCK_UNINDENT', 'STOCK_YES', 'STOCK_ZOOM_100',
'STOCK_ZOOM_FIT', 'STOCK_ZOOM_IN', 'STOCK_ZOOM_OUT',
'terp-account', 'terp-crm', 'terp-mrp', 'terp-product', 'terp-purchase',
'terp-sale', 'terp-tools', 'terp-administration', 'terp-hr', 'terp-partner',
'terp-project', 'terp-report', 'terp-stock', 'terp-calendar', 'terp-graph',
])

main_form = '''<?xml version="1.0"?>
<form string="Select Appropriate Model">
    <field name="model_name"/>
    </form>'''
main_fields = {
    'model_name': {'string':'Model Name', 'type':'many2one', 'relation':'ir.model','required':True},
}

def _cheak_context(self, cr, uid, data, context):
#    context['model']='res.partner'
    if context.has_key('model'):
        if context['model']:
            return 'secondform'
        else:
            return 'firstform'
    else:
        return 'firstform'

def _domain(self, cr, uid, data, context):
    if data['form'].has_key('model_name') and data['form']['model_name']:
        model = pooler.get_pool(cr.dbname).get('ir.model').read(cr, uid,data['form']['model_name'],['model'])
        model_data=model['model']
        return {'in_model_name':model_data}
    else:
        model_data = context['model']
        return {'in_model_name':model_data}


second_form = '''<?xml version="1.0"?>

<form string="Select Appropriate Model View">
    <separator colspan="4" string="Select view and its Sequence" />
    <field name="in_model_name" invisible="True" />
    <field name="form_view" domain="[('inherit_id','=',False),('type','=','form'),('model','=',in_model_name)]"/>
    <field name="form_seq"/>
    <field name="tree_view" domain="[('inherit_id','=',False),('type','=','tree'),('model','=',in_model_name)]"/>
    <field name="tree_seq"/>
    <field name="graph_view" domain="[('inherit_id','=',False),('type','=','graph'),('model','=',in_model_name)]"/>
    <field name="graph_seq"/>
    <field name="calander_view" domain="[('inherit_id','=',False),('type','=','calendar'),('model','=',in_model_name)]"/>
    <field name="cal_seq"/>
</form>'''


second_fields = {
    'in_model_name':{'string':'View Sequence', 'type':'char','size':64, 'readonly':True},
    'form_view': {'string':'Form View', 'type':'many2one','relation':'ir.ui.view'},
    'tree_view': {'string':'Tree View', 'type':'many2one', 'relation':'ir.ui.view'},
    'graph_view': {'string':'Graph View', 'type':'many2one', 'relation':'ir.ui.view'},
    'calander_view': {'string':'Calander View', 'type':'many2one', 'relation':'ir.ui.view'},
    'form_seq': {'string':'Form Sequence', 'type':'integer','size':32},
    'tree_seq': {'string':'Tree Sequence', 'type':'integer','size':32},
    'graph_seq': {'string':'Graph Sequence', 'type':'integer','size':32},
    'cal_seq': {'string':'Calander Sequence', 'type':'integer','size':32},
}

next_form = '''<?xml version="1.0"?>
<form string="Create Menu">
    <field name="menu_name"/>
    <field name="partner_menu"/>
    <field name="sequence"/>
     <field name="icon"/>
    <field name="group" colspan="4"/>
</form>'''

next_fields = {
    'menu_name': {'string':'Menu Name', 'type':'char', 'size':64,'required':True},
    'partner_menu': {'string':'Partner Menu', 'type':'many2one', 'relation':'ir.ui.menu','required':True},
    'sequence': {'string':'Sequence', 'type':'integer', 'size':64,'required':True},
    'group': {'string':'Group', 'type':'many2many', 'relation':'res.groups'},
    'icon': {
        'string': 'Icon',
        'type': 'selection',
        'selection':icons ,
        'default' :lambda *b:'STOCK_JUSTIFY_FILL'
    },
}

def menu_create1(self, cr, uid, data, context):
#    context['model']='res.partner'
    view_mode = 'form,tree'
    icon_data = data['form']['icon'],
    menu_id=pool.get('ir.ui.menu').create(cr, uid, {
        'name': data['form']['menu_name'],
        'parent_id': data['form']['partner_menu'],
        'icon':icon_data[0],
        'sequence':data['form']['sequence'],
        'groups_id':data['form']['group'],
    })
    if data['form'].has_key('model_name') and data['form']['model_name']:
        model = pooler.get_pool(cr.dbname).get('ir.model').read(cr, uid, [data['form']['model_name']],['model'])[0]['model']
    else:
        model=context['model']
    action_id = pooler.get_pool(cr.dbname).get('ir.actions.act_window').create(cr,uid, {
        'name': data['form']['menu_name']+'New',
        'res_model':model,
        'view_type': 'form',
        'view_mode': view_mode,
    })
    if data['form']['form_view']:
        view_action_id = pooler.get_pool(cr.dbname).get('ir.actions.act_window.view').create(cr,uid, {
            'view_mode': 'form',
            'act_window_id':action_id,
            'sequence':data['form']['form_seq'],
            'view_id':data['form']['form_view'],
            })

    if  data['form']['tree_view']:
        view_action_id = pooler.get_pool(cr.dbname).get('ir.actions.act_window.view').create(cr,uid, {
            'view_mode': 'tree',
            'act_window_id':action_id,
            'sequence':data['form']['tree_seq'],
            'view_id':data['form']['tree_view'],
            })

    if  data['form']['graph_view']:
         view_action_id = pooler.get_pool(cr.dbname).get('ir.actions.act_window.view').create(cr,uid, {
            'view_mode': 'graph',
            'act_window_id':action_id,
            'sequence':data['form']['graph_seq'],
            'view_id':data['form']['graph_view'],
            })

    if  data['form']['calander_view']:
         view_action_id = pooler.get_pool(cr.dbname).get('ir.actions.act_window.view').create(cr,uid, {
            'view_mode': 'calendar',
            'act_window_id':action_id,
            'sequence':data['form']['cal_seq'],
            'view_id':data['form']['calander_view'],
            })

    pooler.get_pool(cr.dbname).get('ir.values').create(cr, uid, {
        'name': 'Open Cases',
        'key2': 'tree_but_open',
        'model': 'ir.ui.menu',
        'res_id': menu_id,
        'value': 'ir.actions.act_window,%d'%action_id,
        'object': True
    })
    return {}

class wizard_create_menu(wizard.interface):
    states = {
        'init': {
            'actions': [],
            'result': {'type':'choice','next_state':_cheak_context}
        },
         'firstform': {
            'actions': [],
            'result': {'type':'form', 'arch':main_form, 'fields':main_fields, 'state':[('end','Cancel'),('secondform','Next')]}
        },

        'secondform': {
            'actions': [_domain],
            'result': {'type':'form', 'arch':second_form, 'fields':second_fields, 'state':[('end','Cancel'),('next','Next')]}
        },
        'next': {
            'actions': [],
            'result': {'type':'form', 'arch':next_form, 'fields':next_fields, 'state':[('end','Cancel'),('create','Create menu')]}
        },
        'create': {
            'actions': [menu_create1],
            'result': {'type':'state', 'state':'end'}
        }
    }
wizard_create_menu('create.menu.wizard')
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

