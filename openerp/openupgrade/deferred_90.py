# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2015 Odoo Community Association (OCA)
#    (<https://odoo-community.org>)
#
#    Contributors:
#    - Stefan Rijnhart
#    - Tecnativa - Pedro M. Baeza
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
"""
This module can be used to contain functions that should be called at the end
of the migration. A migration may be run several times after corrections in
the code or the configuration, and there is no way for OpenERP to detect a
succesful result. Therefore, the functions in this module should be robust
against being run multiple times on the same database.
"""
import logging

from openerp import api, models, SUPERUSER_ID
from openerp.osv import fields, orm

from openupgradelib import openupgrade, openupgrade_90, openupgrade_tools


logger = logging.getLogger('OpenUpgrade.deferred')


def disable_invalid_filters(cr):
    with api.Environment.manage():
        env = api.Environment(cr, SUPERUSER_ID, {})
        openupgrade.disable_invalid_filters(env)


def migrate_deferred(cr, pool):
    """ Convert attachment style binary fields """
    logger.info('Deferred migration step called')
    field_spec = {}
    for model_name, model in pool.items():
        if isinstance(model, (orm.TransientModel, models.TransientModel)):
            continue
        for k, v in model._columns.items():
            if (v._type == 'binary' and
                    not isinstance(v, (
                        fields.function, fields.property, fields.related)) and
                    not model._fields[k].company_dependent and
                    v.attachment and
                    openupgrade_tools.column_exists(cr, model._table, k) and
                    (k, k) not in field_spec.get(model_name, [])):
                field_spec.setdefault(model_name, []).append((k, k))

    if field_spec:
        with api.Environment.manage():
            env = api.Environment(cr, SUPERUSER_ID, {})
            openupgrade_90.convert_binary_field_to_attachment(env, field_spec)
    disable_invalid_filters(cr)
