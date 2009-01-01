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

call_list_form = """<?xml version="1.0"?>
<form string="Search form">
    <separator string="Criteria" colspan="4" />
    <field name="city" colspan="4" />
    <field name="categ_id" colspan="4" />
    <separator string="Call case" colspan="4" />
    <field name="section_id" colspan="4" />
    <field name="category_id" colspan="4" />
</form>"""

call_list_fields = {
    'city': {
        'string': 'City',
        'type': 'char',
        'size': 128,
    },
    'categ_id': {
        'string': 'Partner category',
        'type': 'many2one',
        'relation': 'res.partner.category',
        'required': True
    },
    'section_id': {
        'string': 'Section',
        'type': 'many2one',
        'relation': 'crm.case.section',
        'required': True,
    },
    'category_id': {
        'string': 'Category',
        'type': 'many2one',
        'relation': 'crm.case.categ',
        'required': True,
    }
}


class make_call_list(wizard.interface):

    def _make_list(self, cr, uid, data, context):
        print 'OK'
        return {}

    states = {
        'init': {
            'actions': [],
            'result': {
                'type': 'form', 
                'arch': call_list_form, 
                'fields': call_list_fields,
                'state' : [
                    ('end', 'Cancel', 'gtk-cancel'),
                    ('confirm', 'Create', 'gtk-go-forward')
                ]
            }
        },
        'confirm': {
            'actions': [],
            'result': {
                'type': 'action', 
                'action': _make_list, 
                'state': 'end'
            }
        }
    }

make_call_list('partner.call_list')
