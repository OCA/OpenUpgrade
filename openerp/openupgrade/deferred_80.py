# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    This module copyright (C) 2014 Therp BV (<http://therp.nl>)
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
from psycopg2.extensions import AsIs
from openerp import api, SUPERUSER_ID
from openerp.openupgrade import openupgrade
logger = logging.getLogger('OpenUpgrade.deferred')


def migrate_product_valuation(cr, pool):
    """Migrate the product valuation to a property field on product template.
    This field was moved to a new module which is not installed when the
    migration starts and thus not upgraded, which is why we do it here in the
    deferred step.

    This method removes the preserved legacy column upon success, to prevent
    double runs which would be harmful.
    """
    valuation_column = openupgrade.get_legacy_name('valuation')
    if not openupgrade.column_exists(cr, 'product_product', valuation_column):
        return

    cr.execute(
        """
        SELECT id FROM ir_model_fields
        WHERE model = 'product.template' AND name = 'valuation'
        """)
    field_id = cr.fetchone()[0]

    property_obj = pool['ir.property']
    default = 'manual_periodic'  # as per stock_account/stock_account_data.xml

    cr.execute(
        """
        SELECT product_tmpl_id, {column} FROM product_product
        WHERE {column} != %s""".format(column=valuation_column),
        (default,))
    products = cr.fetchall()
    logger.debug(
        "Migrating the valuation field of %s products with non-default values",
        len(products))

    seen_ids = []
    for template_id, value in products:
        if not value or template_id in seen_ids:
            continue
        seen_ids.append(template_id)
        property_obj.create(
            cr, SUPERUSER_ID, {
                'fields_id': field_id,
                'company_id': False,
                'res_id': 'product.template,{}'.format(template_id),
                'name': 'Valuation Property',
                'type': 'selection',
                'value_text': value,
                })

    cr.execute(
        "ALTER TABLE product_product DROP COLUMN {}".format(valuation_column))


def migrate_procurement_order_method(env):
    """Procurements method: change the supply_method for the matching rule

    Needs to be deferred because the rules are created in the migration
    of stock, purchase and mrp.

    Will only run if stock is installed. Will run after every attempt to
    upgrade, but harmless when run multiple times.
    """

    env.cr.execute(
        """
        SELECT id FROM ir_module_module
        WHERE name = 'stock' AND state = 'installed'
        AND latest_version = '8.0.1.1'
        """)
    if not env.cr.fetchone():
        # Only warn if there are traces of stock
        if openupgrade.table_exists(env.cr, 'stock_move'):
            logger.debug(
                "Stock not installed or not properly migrated, skipping "
                "migration of procurement orders.")
        return

    procure_method_legacy = openupgrade.get_legacy_name('procure_method')
    if not openupgrade.column_exists(
            env.cr, 'product_template', procure_method_legacy):
        # in this case, there was no migration for the procurement module
        # which can be okay if procurement was not installed in the 7.0 db
        return

    mto_route_id = env['stock.warehouse']._get_mto_route()

    env.cr.execute(
        """ SELECT ARRAY_AGG(po.id), po.%(procure_method)s,
            pt.%(supply_method)s, po.location_id, sm.location_dest_id
        FROM procurement_order po
            JOIN product_product pp ON po.product_id = pp.id
            JOIN product_template pt ON pp.product_tmpl_id = pt.id
            LEFT JOIN stock_move sm ON po.id = sm.procurement_id
        WHERE po.rule_id is NULL AND po.state != 'done'
        GROUP BY po.%(procure_method)s, pt.%(supply_method)s, po.location_id,
            sm.location_dest_id """, {
                'procure_method': AsIs(procure_method_legacy),
                'supply_method': AsIs(
                    openupgrade.get_legacy_name('supply_method')),
            })

    parent_location_cache = {}

    def get_parent_locations(location_in):
        if location_in not in parent_location_cache:
            location = locations = location_in
            while location.location_id:
                location = location.location_id
                locations += location
            parent_location_cache[location_in] = locations
        return parent_location_cache[location_in]

    for (proc_ids, procure_method, supply_method, location_id,
         location_dest_id) in env.cr.fetchall():
        location_dest = env['stock.location'].browse(location_dest_id)
        procurement = env['procurement.order'].browse(proc_ids[0])
        procurement_repr = '%s procurements (%s -> %s, %s, %s)' % (
            len(proc_ids), procurement.location_id.complete_name,
            location_dest.complete_name or ' - ', procure_method, supply_method)

        rule = False
        if location_dest and procure_method == 'make_to_stock':
            # Prefer move rules if there is one between the two locations
            parent_dest_locations = get_parent_locations(location_dest)
            parent_locations = get_parent_locations(
                env['stock.location'].browse(location_id))
            rule = env['procurement.rule'].search([
                ('location_id', 'in', parent_dest_locations.ids),
                ('location_src_id', 'in', parent_locations.ids),
                ('action', '=', 'move'),
                ('route_id', '!=', mto_route_id)], limit=1)

        if not rule:
            rule_id = env['procurement.order']._find_suitable_rule(procurement)
            if rule_id:
                rule = env['procurement.rule'].browse(rule_id)

        if rule:
            logger.info(
                'Got rule %s (%s->%s) for %s',
                rule.name, rule.location_src_id.complete_name,
                rule.location_id.complete_name, procurement_repr)
            env['procurement.order'].browse(proc_ids).write(
                {'rule_id': rule.id})
        else:
            logger.warn(
                'No rule found for %s. Please create and assign a new rule '
                'for this configuration.', procurement_repr)


def migrate_stock_move_warehouse(cr):
    """
    If a database featured multiple shops with the same company but a
    different warehouse, we can now propagate this warehouse to the
    associated stock moves. The warehouses were written on the procurements
    in the sale_stock module, while the moves were associated with the
    procurements in purchase and mrp. The order of processing between
    these modules seems to be independent, which is why we do this here
    in the deferred step.
    """
    cr.execute(
        "SELECT * FROM ir_module_module WHERE name='stock' "
        "AND state='installed'")
    if not cr.fetchone():  # No stock
        return
    openupgrade.logged_query(
        cr,
        """
        UPDATE stock_move sm
        SET warehouse_id = po.warehouse_id
        FROM procurement_order po
        WHERE sm.procurement_id = po.id
            OR po.move_dest_id = sm.id
        """)


def migrate_deferred(cr, pool):
    env = api.Environment(cr, SUPERUSER_ID, {})
    migrate_product_valuation(cr, pool)
    migrate_procurement_order_method(env)
    migrate_stock_move_warehouse(cr)
