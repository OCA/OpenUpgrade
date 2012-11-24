# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    This module copyright (C) 2011-2012 Therp BV (<http://therp.nl>)
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

import types
from openerp.osv.orm import TransientModel
from openerp.openupgrade.openupgrade import table_exists

# A collection of functions used in 
# openerp/modules/loading.py

def add_module_dependencies(cr, module_list):
    """
    Select (new) dependencies from the modules in the list
    so that we can inject them into the graph at upgrade
    time. Used in the modified OpenUpgrade Server,
    not to be used in migration scripts
    """
    if not module_list:
        return module_list
    cr.execute("""
        SELECT ir_module_module_dependency.name
        FROM
            ir_module_module,
            ir_module_module_dependency
        WHERE
            module_id = ir_module_module.id
            AND ir_module_module.name in %s
        """, (tuple(module_list),))
    dependencies = [x[0] for x in cr.fetchall()]
    return list(set(module_list + dependencies))

def log_model(model, local_registry):
    """
    OpenUpgrade: Store the characteristics of the BaseModel and its fields
    in the local registry, so that we can compare changes with the
    main registry
    """

    if not model._name: # new in 6.1
        return

    # persistent models only
    if isinstance(model, TransientModel):
        return

    model_registry = local_registry.setdefault(
            model._name, {})
    if model._inherits:
        model_registry['_inherits'] = {'_inherits': unicode(model._inherits)}
    for k, v in model._columns.items():
        properties = { 
            'type': v._type,
            'isfunction': (
                isinstance(v, osv.fields.function) and 'function' or ''),
            'relation': (
                v._type in ('many2many', 'many2one','one2many')
                and v._obj or ''
                ),
            'required': v.required and 'required' or '',
            'selection_keys': '',
            'req_default': '',
            'inherits': '',
            }
        if v._type == 'selection':
            if hasattr(v.selection, "__iter__"):
                properties['selection_keys'] = unicode(
                    sorted([x[0] for x in v.selection]))
            else:
                properties['selection_keys'] = 'function'
        if v.required and k in model._defaults:
            if isinstance(model._defaults[k], types.FunctionType):
                # todo: in OpenERP 5 (and in 6 as well),
                # literals are wrapped in a lambda function
                properties['req_default'] = 'function'
            else:
                properties['req_default'] = unicode(
                    model._defaults[k])
        for key, value in properties.items():
            if value:
                model_registry.setdefault(k, {})[key] = value

def get_record_id(cr, module, model, field, mode):
    """
    OpenUpgrade: get or create the id from the record table matching
    the key parameter values
    """
    cr.execute(
        "SELECT id FROM openupgrade_record "
        "WHERE module = %s AND model = %s AND "
        "field = %s AND mode = %s AND type = %s",
        (module, model, field, mode, 'field')
        )
    record = cr.fetchone()
    if record:
        return record[0]
    cr.execute(
        "INSERT INTO openupgrade_record "
        "(module, model, field, mode, type) "
        "VALUES (%s, %s, %s, %s, %s)",
        (module, model, field, mode, 'field')
        )
    cr.execute(
        "SELECT id FROM openupgrade_record "
        "WHERE module = %s AND model = %s AND "
        "field = %s AND mode = %s AND type = %s",
        (module, model, field, mode, 'field')
        )
    return cr.fetchone()[0]

def compare_registries(cr, module, registry, local_registry):
    """
    OpenUpgrade: Compare the local registry with the global registry,
    log any differences and merge the local registry with
    the global one.
    """
    if not table_exists(cr, 'openupgrade_record'):
        return
    for model, fields in local_registry.items():
        registry.setdefault(model, {})
        for field, attributes in fields.items():
            old_field = registry[model].setdefault(field, {})
            mode = old_field and 'modify' or 'create'
            record_id = False
            for key, value in attributes.items():
                if key not in old_field or old_field[key] != value:
                    if not record_id:
                        record_id = get_record_id(
                            cr, module, model, field, mode)
                    cr.execute(
                        "SELECT id FROM openupgrade_attribute "
                        "WHERE name = %s AND value = %s AND "
                        "record_id = %s",
                        (key, value, record_id)
                        )
                    if not cr.fetchone():
                        cr.execute(
                            "INSERT INTO openupgrade_attribute "
                            "(name, value, record_id) VALUES (%s, %s, %s)",
                            (key, value, record_id)
                            )
                    old_field[key] = value
