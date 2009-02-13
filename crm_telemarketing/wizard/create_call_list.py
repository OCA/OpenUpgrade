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

from tools.translate import _

#
# First Form
#
call_list_form = """<?xml version="1.0"?>
<form string="Search form">
    <separator string="Criteria" colspan="4" />
    <field name="city" colspan="4" />
    <field name="categ_id" colspan="4" />
    <separator string="Call case" colspan="4" />
    <field name="section_id" colspan="4" />
    <field name="category_id" colspan="4" domain="[('section_id','=',section_id)]"/>
    <field name="date_call" colspan="4" />
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
    },
    'date_call': {
        'string': 'Plan call date',
        'type': 'date',
    },
}

#
# Second Form
#
result_form = """<?xml version="1.0"?>
<form string="Result">
<field name="message" nolabel="1" colspan="4" width="600"/>
</form>"""

result_fields = {
    'message': {
        'string': 'message',
        'type': 'char',
        'size': 128,
        'readonly': True,
    },
}

class make_call_list(wizard.interface):

    def _make_list(self, cr, uid, data, context):
        form = data['form']
        pool = pooler.get_pool(cr.dbname)

        query = """SELECT DISTINCT add.partner_id FROM
        (SELECT partner_id FROM res_partner_category_rel WHERE category_id=%s) cat,
        res_partner_address add
        WHERE add.partner_id=cat.partner_id""" % form['categ_id']

        if form['city']:
            query += " AND city ilike '%s%%'" % form['city']

        # Search all match record
        cr.execute(query)
        
        partner_obj = pool.get('res.partner')
        address_obj = pool.get('res.partner.address')
        case_obj = pool.get('crm.case')
        x = 0
        for r in cr.fetchall():
            x += 1
            partner = partner_obj.read(cr, uid, r, ['name'], context)[0]

            args = [('partner_id','=',r)]
            addr_id = address_obj.search(cr, uid, args)[0]
            if addr_id:
                addr = address_obj.read(cr, uid, addr_id, ['phone','mobile'], context)

            case = {
                'name': partner['name'],
                'section_id': form['section_id'],
                'categ_id': form['category_id'],
                'partner_id': r[0],
                'partner_phone': False,
                'partner_mobile': False,
                'user_id': False,
            }

            if addr_id:
                case['partner_phone'] = addr['phone']
                case['partner_mobile'] = addr['mobile']

            if form['date_call']:
                case['date'] = form['date_call']

            case_id = case_obj.create(cr, uid, case, context)
            #if not case_id:

        result = '%i appel(s) crée(s)' % x
        return {'message': result}

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
            'actions': [_make_list],
            'result': {
                'type': 'form', 
                'arch': result_form,
                'fields': result_fields,
                'state': [
                    ('end', 'OK', 'gtk-ok', True),
                ]
            }
        }
    }

make_call_list('partner.call_list')
