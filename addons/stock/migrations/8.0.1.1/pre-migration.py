# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2014 ONESTEiN B.V.
#              (C) 2014 Therp B.V.
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

import logging
from openerp.openupgrade import openupgrade


logger = logging.getLogger('OpenUpgrade.stock')

column_renames = {
    'product_product': [
        ('track_incoming', None),
        ('track_outgoing', None),
        ('track_production', None),
        ('valuation', None)
    ],
    'stock_inventory': [
        ('date_done', None),
    ],
    'stock_inventory_line': [
        ('product_uom', 'product_uom_id'),
    ],
    'stock_move': [
        ('auto_validate', None),
        ('price_currency_id', None),
        ('prodlot_id', None),
        ('product_qty', 'product_uom_qty'),
        ('tracking_id', None)
    ],
    'stock_production_lot': [
        ('company_id', None),
        ('create_date', None),
        ('date', 'create_date'),
        ('prefix', None)
    ],
    'stock_picking': [
        ('type', None),
    ],
    'stock_location': [
        ('icon', None),
        ('chained_journal_id', None),
        ('chained_location_id', None),
        ('chained_location_type', None),
        ('chained_auto_packing', None),
        ('chained_company_id', None),
        ('chained_delay', None),
        ('chained_picking_type', None),
    ],
    'stock_warehouse': [
        ('lot_input_id', 'wh_input_stock_loc_id'),
        ('lot_output_id', 'wh_output_stock_loc_id'),
    ],
    'stock_warehouse_orderpoint': [
        ('product_uom', None),
    ],
}

xmlid_renames = [
    ('procurement.sequence_mrp_op_type', 'stock.sequence_mrp_op_type'),
    ('procurement.sequence_mrp_op', 'stock.sequence_mrp_op'),
    ('stock.property_stock_account_input_categ',
        'stock_account.property_stock_account_input_categ'),
    ('stock.property_stock_account_input_prd',
        'stock_account.property_stock_account_input_prd'),
    ('stock.property_stock_account_output_categ',
        'stock_account.property_stock_account_output_categ'),
    ('stock.property_stock_account_output_prd',
        'stock_account.property_stock_account_output_prd'),
    ('stock.property_stock_journal', 'stock_account.property_stock_journal'),
    ('stock.stock_journal', 'stock_account.stock_journal'),
    ('stock.group_inventory_valuation',
        'stock_account.group_inventory_valuation'),
    ('stock.stock_journal_sequence',
        'stock_account.stock_journal_sequence'),
]


def initialize_location_inventory(cr):
    """Stock Inventory is upgraded before Stock Warehouse. The default value
    of the field location_id (triggered by a missing NOT NULL constraint)
    is searched in the stock_warehouse table, asking
    for columns that has not been created yet because of the browse object.
    Therefore, precreate the column and fill with values from its own lines.
    Fallback on the stock location of the inventory's company's warehouse.
    """
    cr.execute("ALTER TABLE stock_inventory ADD COLUMN location_id INTEGER")
    openupgrade.logged_query(
        cr,
        """
        UPDATE stock_inventory si
        SET location_id = l.location_id
        FROM stock_inventory_line l
        WHERE l.inventory_id = si.id
        """)
    openupgrade.logged_query(
        cr,
        """
        UPDATE stock_inventory si
        SET location_id = sw.lot_stock_id
        FROM stock_warehouse sw
        WHERE location_id is NULL
            AND (si.company_id = sw.company_id
                 OR sw.company_id is NULL)
        """)
    cr.execute("ALTER TABLE stock_inventory "
               "ALTER COLUMN location_id SET NOT NULL")


def create_stock_picking_fields(cr):
    """ This function reduce creation time of the stock_picking fields
    """
    logger.info("Fast creation of the field stock_picking.priority")
    cr.execute("""
        ALTER TABLE stock_picking
        ADD COLUMN "priority" VARCHAR DEFAULT '1'""")
    # This request do the same as stock_picking.get_min_max_date but faster
    openupgrade.logged_query(cr, """
        UPDATE stock_picking sp set priority = res.priority
        FROM (
            SELECT picking_id, max(priority) as priority
            FROM stock_move
            WHERE priority > '1'
            GROUP BY picking_id) as res
        WHERE sp.id = res.picking_id""")
    logger.info("Fast creation of the field stock_picking.group_id")
    cr.execute("""
        ALTER TABLE stock_picking
        ADD COLUMN "group_id" integer""")
    # Note, we don't set values because stock_picking group_id is a fields
    # related to stock_move group_id that is a new field.


def create_stock_move_fields(cr):
    """ This function reduce creation time of the stock_move fields
       This part of the function (pre) just create the field and let
       the other function in post script fill the value, because orm is needed
    """
    logger.info("Fast creation of the field stock_move.product_qty (pre)")
    # This field is a functional field, the value will be set at the
    # beginning of the post script;
    cr.execute("""
        ALTER TABLE stock_move
        ADD COLUMN "product_qty" NUMERIC""")
    logger.info("Fast creation of the field stock_move.propagate")
    cr.execute("""
        ALTER TABLE "stock_move"
        ADD COLUMN "propagate" bool DEFAULT True""")
    logger.info("Fast creation of the field stock_move.procure_method")
    cr.execute("""
        ALTER TABLE "stock_move"
        ADD COLUMN "procure_method" VARCHAR DEFAULT 'make_to_stock'""")


@openupgrade.migrate()
def migrate(cr, version):
    openupgrade.rename_columns(cr, column_renames)
    openupgrade.rename_xmlids(cr, xmlid_renames)
    initialize_location_inventory(cr)
    openupgrade.rename_tables(cr, [('stock_inventory_move_rel', None)])

    create_stock_picking_fields(cr)
    create_stock_move_fields(cr)
