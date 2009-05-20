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

from tools.misc import UpdateableStr, UpdateableDict
from tools.translate import _
import ir
import pooler
import time
import wizard


comp_type_form = '''<?xml version="1.0"?>
    <form string="Select Component Type">
        <field name="compnent_type_id"/>
    </form>''' 

comp_type_fields = {
    'compnent_type_id' : {'string':'Component Type', 'type':'many2one', 'relation': 'etl.component.type','required':True}
}

COMP_FORM = UpdateableStr()
FIELDS = UpdateableDict()

def _add_component(self, cr, uid, data, context):
    pool = pooler.get_pool(cr.dbname)
    job_obj = pool.get('etl.job')
    comp_obj = pool.get('etl.component')
    val = data['form']
    val['type_id'] = val['compnent_type_id']
    del val['compnent_type_id']
    for job in job_obj.browse(cr, uid, data['ids'], context):
        val['job_id'] =  job.id
        comp_id = comp_obj.create(cr, uid, data['form'])
    return {}

def _get_view(self, cr, uid, data, context):
    pool = pooler.get_pool(cr.dbname)
    job_obj = pool.get('etl.job')
    comp_obj = pool.get('etl.component')
    comp_type_obj = pool.get('etl.component.type')
    comptype =comp_type_obj.browse(cr, uid,data['form']['compnent_type_id'] )
    view_name = 'view.etl.component.' +comptype.name
    cr.execute("select id, arch from ir_ui_view where name = '%s'" % view_name)
    data = cr.dictfetchall()
    if not data:
        cr.execute("select id, arch from ir_ui_view where name = 'view.etl.component.form'")
        data = cr.dictfetchall()
    view_id = data[0]['id']
    result = comp_obj.fields_view_get(cr, uid, view_id, 'form', context={})
    for f in result['fields']:
        FIELDS[f] = {
                'string': result['fields'][f]['string'],
                'type' : result['fields'][f]['type'],
                     }
        if result['fields'][f]['type'] in ['many2one', 'many2many', 'one2many']:
            FIELDS[f].update({'relation' : result['fields'][f]['relation']})
        if result['fields'][f]['type'] == 'char':
            FIELDS[f].update({'size' : 64})
        if result['fields'][f]['type'] == 'selection':
            FIELDS[f].update({'selection' : result['fields'][f]['selection']})
    COMP_FORM.string =  data[0]['arch']
    return {}

def _check_state(self, cr, uid, data, context):
    job_obj = pooler.get_pool(cr.dbname).get('etl.job')
    job = job_obj.browse(cr, uid, data['ids'])[0]

    if not job.state in ('draft'):
        raise wizard.except_wizard(_('Job not in draft state !'), _('You can not add components in job which is in "%s" state') % job.state.upper())
    return {}

class add_component(wizard.interface):
    states = {
        'init' : {
            'actions' : [_check_state],
            'result' : {'type' : 'form', 'arch' : comp_type_form, 'fields' : comp_type_fields, 'state' : [('end', '_Cancel', 'gtk-cancel'),('view', '_Next', 'gtk-go-forward') ]}
        },
        'view' : {
            'actions' : [_get_view],
            'result' : {'type': 'form', 'arch': COMP_FORM, 'fields': FIELDS, 'state' : [('end', '_Cancel', 'gtk-cancel'),('save', '_Save', 'gtk-save') ]}
            },
        'save' : {
            'actions' : [],
            'result' : {'type' : 'action', 'action' : _add_component, 'state' : 'end'}
        },
        
    }
add_component("etl.job.add_component")

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
