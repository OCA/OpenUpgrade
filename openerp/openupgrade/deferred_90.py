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


def set_so_line_computed_invoicing_fields(env):
    """ Depends on correct values for qty_delivered
    as computed in sale_stock and sale_mrp """
    logger.info(
        'Computing invoicing related stored fields on sale order lines')
    uom_precision = env['decimal.precision'].precision_get(
        'Product Unit of Measure')
    openupgrade.logged_query(
        env.cr, """
        UPDATE sale_order_line sol
        SET qty_to_invoice = (CASE
            WHEN so.state IN ('sale', 'done')
                THEN (CASE
                    WHEN pt.invoice_policy = 'order'
                        THEN sol.product_uom_qty - sol.qty_invoiced
                    ELSE sol.qty_delivered - sol.qty_invoiced
                END)
            ELSE 0.0
        END)
        FROM sale_order_line sol2
            JOIN sale_order so ON so.id = sol2.order_id
            JOIN product_product pp ON pp.id = sol2.product_id
            JOIN product_template pt ON pt.id = pp.product_tmpl_id
        WHERE sol2.id = sol.id""")
    openupgrade.logged_query(
        env.cr, """
        UPDATE sale_order_line sol
        SET invoice_status = CASE
            WHEN sol.state NOT IN ('sale', 'done') THEN 'no'
            WHEN ROUND(sol.qty_to_invoice, %(uom_precision)s) != 0
                THEN 'to invoice'
            WHEN sol.state = 'sale' AND pt.invoice_policy = 'order' AND
                ROUND(sol.qty_delivered, %(uom_precision)s) >
                    ROUND(sol.product_uom_qty, %(uom_precision)s)
                    THEN 'upselling'
            WHEN ROUND(sol.qty_invoiced, %(uom_precision)s) >=
                ROUND(sol.product_uom_qty, %(uom_precision)s)
                THEN 'invoiced'
            ELSE 'no'
        END
        FROM sale_order_line sol2
            JOIN product_product pp ON pp.id = sol2.product_id
            JOIN product_template pt ON pt.id = pp.product_tmpl_id
        WHERE sol2.id = sol.id""",
        {"uom_precision": uom_precision})
    openupgrade.logged_query(
        env.cr, """
        UPDATE sale_order so
        SET invoice_status = CASE
            WHEN so.state NOT IN ('sale', 'done') THEN 'no'
            -- Check if at least there's one line to invoice
            WHEN 'to invoice' = ANY(
                    SELECT invoice_status FROM sale_order_line sol
                    WHERE sol.order_id = so.id
                )
                THEN 'to invoice'
            -- Check if all lines are invoiced
            WHEN 'invoiced' = ALL(
                    SELECT invoice_status
                    FROM sale_order_line sol
                    WHERE sol.order_id = so.id
                )
                THEN 'invoiced'
            WHEN
                -- Check if all lines are either invoiced or upselling
                0 = (
                    SELECT COUNT(*)
                    FROM sale_order_line sol
                    WHERE sol.order_id = so.id
                    AND sol.invoice_status NOT IN ('invoiced', 'upselling')
                -- ... and that at least one is upselling
                ) AND 'upselling' = ANY(
                    SELECT invoice_status
                    FROM sale_order_line sol
                    WHERE sol.order_id = so.id
                )
                THEN 'upselling'
            ELSE 'no'
        END""")


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

    with api.Environment.manage():
        env = api.Environment(cr, SUPERUSER_ID, {})
        if openupgrade.is_module_installed(env.cr, 'sale'):
            set_so_line_computed_invoicing_fields(env)
        if field_spec:
            openupgrade_90.convert_binary_field_to_attachment(env, field_spec)
    disable_invalid_filters(cr)
