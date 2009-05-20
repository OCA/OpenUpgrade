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


TRANS_FORM = """<?xml version="1.0"?>
                    <form string="Transition">
                        <field name="name" select="1" />
                        <field name="type" select="1" />
                        <separator string="Transition property" colspan="4" />
                        <newline />
                        <field name="source_component_id" select="1" />
                        <field name="destination_component_id" select="1" />
                        <field name="channel_source" select="1" />
                        <field name="channel_destination" select="1" />
                        <separator string="Status" colspan="4" />
                        <newline />
                        <field name="state" select="1" />
                    </form>"""

trans_fields = {
                'name' : {'required': True, 'type': 'char', 'string': 'Name', 'size': 64} ,
                'channel_source' : {'selection': [('main', 'main'), ('error', 'error'), ('gmail', 'gmail'), ('partner', 'partner'), ('address', 'address')], 'type': 'selection', 'string': 'Source Channel'} ,
                'state' : {'readonly': True, 'selection': [('open', 'Open'), ('close', 'Close')], 'type': 'selection', 'string': 'State', 'default' : lambda *a: 'open'} ,
                'channel_destination' : {'selection': [('main', 'main'), ('error', 'error'), ('gmail', 'gmail'), ('partner', 'partner'), ('address', 'address')], 'type': 'selection', 'string': 'Destination Channel'} ,
                'destination_component_id' : { 'string': 'Destination Component', 'views': {}, 'required': True, 'relation': 'etl.component', 'type': 'many2one'} ,
                'source_component_id' : {'string': 'Source Component', 'views': {}, 'required': True, 'relation': 'etl.component', 'context': '', 'type': 'many2one'} ,
                'type' : {'selection': [('data', 'Data Transition'), ('trigger', 'Trigger Transition')], 'required': True, 'type': 'selection', 'string': 'Transition Type'} ,
                }

def _add_transition(self, cr, uid, data, context):
    trans_obj = pooler.get_pool(cr.dbname).get('etl.transition')
    trans_id = trans_obj.create(cr, uid, data['form'])
    return {}

def _get_domain(self, cr, uid, data, context):
    trans_fields['destination_component_id']['domain'] =   [('job_id','=',data['ids'])]
    trans_fields['source_component_id']['domain'] =   [('job_id','=',data['ids'])]
    return {}

def _check_state(self, cr, uid, data, context):
    job_obj = pooler.get_pool(cr.dbname).get('etl.job')
    job = job_obj.browse(cr, uid, data['ids'])[0]
    if not job.state in ('draft'):
        raise wizard.except_wizard(_('Job not in draft state !'), _('You can not add transitions in job which is in "%s" state') % job.state.upper())
    if len(job.component_ids) < 2:
        raise wizard.except_wizard(_('No enough Components !'), _('You need at-least  two component to add transition'))
    return {}

class add_component(wizard.interface):
    states = {
        'init' : {
            'actions' : [_check_state,_get_domain],
            'result' : {'type' : 'form', 'arch' : TRANS_FORM, 'fields' : trans_fields, 'state' : [('end', '_Cancel', 'gtk-cancel'),('save', '_Save', 'gtk-save')]}
        },
        'save' : {
            'actions' : [],
            'result' : {'type' : 'action', 'action' : _add_transition, 'state' : 'end'}
        },
        
    }
add_component("etl.job.add_transitions")

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: