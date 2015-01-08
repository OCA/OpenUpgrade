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
from openerp import SUPERUSER_ID
from openerp.openupgrade import openupgrade
logger = logging.getLogger('OpenUpgrade.deferred')


def migrate_product_valuation(cr, pool):
    """Migrate the product valuation to a property field onproduct template.
    This field also moved to a new module which is not installed when the
    migration starts and thus not upgraded.

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


def migrate_procurement_order_method(cr, pool):
    """Procurements method: change the supply_method for the matching rule

    Needs to be deferred because the rules are created in the migration
    of stock, purchase and mrp.

    Will only run if stock is installed. Will run after every attempt to
    upgrade, but harmless when run multiple times.
    """

    cr.execute(
        """
        SELECT id FROM ir_module_module
        WHERE name = 'stock' AND state = 'installed'
        AND latest_version = '8.0.1.1'
        """)
    if not cr.fetchone():
        # Only warn if there are traces of stock
        if openupgrade.table_exists(cr, 'stock_move'):
            logger.debug(
                "Stock not installed or not properly migrated, skipping "
                "migration of procurement orders.")
        return

    procure_method_legacy = openupgrade.get_legacy_name('procure_method')
    if not openupgrade.column_exists(
            cr, 'product_template', procure_method_legacy):
        # in this case, there was no migration for the procurement module
        # which can be okay if procurement was not installed in the 7.0 db
        return

    procurement_obj = pool['procurement.order']
    rule_obj = pool['procurement.rule']
    rules = {}
    for rule in rule_obj.browse(
            cr, SUPERUSER_ID,
            rule_obj.search(cr, SUPERUSER_ID, [])):
        rules.setdefault(
            rule.location_id.id, {})[rule.procure_method] = rule.id
        rules.setdefault(rule.location_id.id, {})[rule.action] = rule.id

    cr.execute(
        """
        SELECT pp.id FROM product_product pp, product_template pt
        WHERE pp.product_tmpl_id = pt.id
            AND pt.%s = 'produce'
        """ % openupgrade.get_legacy_name('supply_method'))
    production_products = [row[0] for row in cr.fetchall()]

    cr.execute(
        """
        SELECT id, %s FROM procurement_order
        WHERE rule_id is NULL AND state != %%s
        """ % procure_method_legacy, ('done',))

    procurements = cr.fetchall()
    if len(procurements):
        logger.debug(
            "Trying to find rules for %s procurements", len(procurements))

    for proc_id, procure_method in procurements:
        procurement = procurement_obj.browse(cr, SUPERUSER_ID, proc_id)
        location_id = procurement.location_id.id

        # if location type is internal (presumably stock), then
        # find the rule with this location and the appropriate action,
        # regardless of procure method
        rule_id = False
        action = 'move'  # Default, only for log message
        if procure_method == 'make_to_order':
            if procurement.location_id.usage == 'internal':
                if procurement.product_id.id in production_products:
                    action = 'manufacture'
                else:
                    action = 'buy'
                rule_id = rules.get(location_id).get(action)
            else:
                rule_id = rules.get(location_id).get('make_to_order')
        else:
            rule_id = rules.get(location_id).get('make_to_stock')
        if rule_id:
            procurement.write({'rule_id': rule_id})
        else:
            logger.warn(
                "Procurement order #%s with location %s "
                "has no %s procurement rule with action %s, please create and "
                "assign a new rule for this procurement""",
                procurement.id, procurement.location_id.name,
                procure_method, action)


def migrate_stock_move_warehouse(cr):
    """
    If a database featured multiple shops with the same company but a
    different warehouse, we can now propagate this warehouse to the
    associated stock moves. The warehouses were written on the procurements
    in the sale_stock module, while the moves were associated with the
    procurements in various modules.
    """
    cr.execute(
        "SELECT count(*) FROM ir_module_module WHERE name='stock' "
        "AND state='installed'")
    if not cr.fetchone(): # No stock
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
    migrate_product_valuation(cr, pool)
    migrate_procurement_order_method(cr, pool)
    migrate_stock_move_warehouse(cr)
