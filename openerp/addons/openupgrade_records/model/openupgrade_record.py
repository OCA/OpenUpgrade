# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    This module Copyright (C) 2012 OpenUpgrade community
#    https://launchpad.net/~openupgrade-committers
#
#    Contributors:
#    Therp BV <http://therp.nl>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from osv import osv, fields

# Cannot use forward references in 6.0
class openupgrade_record(osv.osv):
    _name = 'openupgrade.record'
openupgrade_record()

class openupgrade_attribute(osv.osv):
    _name = 'openupgrade.attribute'
    _rec_name = 'name'
    _columns = {
        'name': fields.char(
            'Name', size=24,
            readonly=True,
            ),
        'value': fields.char(
            'Value',
            size=4096,
            readonly=True,
            ),
        'record_id': fields.many2one(
            'openupgrade.record', ondelete='CASCADE',
            readonly=True,
            ),
        }
openupgrade_attribute()

class openupgrade_record(osv.osv):
    _inherit = 'openupgrade.record'

    _columns = {
        'name': fields.char('Name', size=256, readonly=True),
        'module': fields.char('Module', size=128, readonly=True),
        'model': fields.char('Model', size=128, readonly=True),
        'field': fields.char('Field', size=128, readonly=True),
        'mode': fields.selection(
            [('create', 'Create'), ('modify', 'Modify')],
            'Mode',
            help='Set to Create if a field is newly created '
            'in this module. If this module modifies an attribute of an '
            'exting field, set to Modify.',
            readonly=True,
             ),
        'type': fields.selection(
            [('field', 'Field'), ('xmlid', 'XML ID')],
            'Type',
            readonly=True,
            ),
        'attribute_ids': fields.one2many(
            'openupgrade.attribute', 'record_id', 'Attributes',
            readonly=True,
            ),
        }
    def field_dump(self, cr, uid, context=None):
        keys = [
            'module',
            'mode',
            'model',
            'field',
            'type',
            'isfunction',
            'relation',
            'required',
            'selection_keys',
            'req_default',
            'inherits',
            ]

        template = dict([(x, False) for x in keys])
        ids = self.search(cr, uid, [('type', '=', 'field')], context=context)
        records = self.browse(cr, uid, ids, context=context)
        data = []
        for record in records:
            repr = template.copy()
            repr.update({
                    'module': record.module,
                    'model': record.model,
                    'field': record.field,
                    'mode': record.mode,
                    })
            repr.update(
                dict([(x.name, x.value) for x in record.attribute_ids]))
            data.append(repr)
        return data

openupgrade_record()
