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
import threading
import pooler

parameter_form = '''<?xml version="1.0"?>
<form string="Create View" colspan="4">
    <label string="Create component's view from type" />
</form>'''

parameter_fields = {
}

def _create_view(self, cr, uid, data, context):
    type_obj = pooler.get_pool(cr.dbname).get('etl.component.type')
    type_obj.add_type_view(cr, uid, data['ids'])
    return {}

class create_component_view(wizard.interface):
    states = {
        'init': {
            'actions': [],
            'result': {'type': 'form', 'arch':parameter_form, 'fields': parameter_fields, 'state':[('end','Cancel'),('create','Create') ]}
        },
        'create': {
            'actions': [_create_view],
            'result': {'type': 'state', 'state':'end'}
        },
    }
create_component_view('etl.component.type.add_fields')

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

