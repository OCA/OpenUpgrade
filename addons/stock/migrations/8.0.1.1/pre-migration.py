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


def swap_procurement_move_rel(cr):
    """
    In 7.0:
    procurement_order.move_id: the reservation for which the procurement
    was generated. Counterpart field on the stock
    move is stock_move.procurements. This is the move_dest_id on the
    purchase order lines that are created for the procurement, which is
    propagated as the move_dest_id on the move lines created for the incoming
    products of the purchase order. The id(s) of these move lines are recorded
    as the purchase line's move_ids (or stock_move.purchase_line_id).

    Something similar occurs in mrp: stock_move.production_id vs. production_
    order.move_created_ids(2), and procurement_order.production_id. The
    procurement order's move_id is production_order.move_prod_id.

    In 8.0:
    procurement_order.move_dest_id: stock move that generated the procurement
    order, e.g. a sold product from stock to customer location. Counterpart
    field on the stock move does not seem to exist.
    procurement_order.move_ids: moves that the procurement order has generated,
    e.g. a purchased product from supplier to stock location. Counterpart field
    on the stock move is stock_move.procurement_id.

    Here, we only rename the move_id column. We need to gather the
    procurement's move_ids in purchase and mrp.
    """
    move_id_column = openupgrade.get_legacy_name('move_id')
    openupgrade.rename_columns(
        cr, {'procurement_order': [(move_id_column, 'move_dest_id')]})


@openupgrade.migrate()
def migrate(cr, version):
    openupgrade.rename_columns(cr, column_renames)
    openupgrade.rename_xmlids(cr, xmlid_renames)
    initialize_location_inventory(cr)
    openupgrade.rename_tables(cr, [('stock_inventory_move_rel', None)])

    have_procurement = openupgrade.column_exists(
        cr, 'product_template', openupgrade.get_legacy_name('procure_method'))
    if have_procurement:
        swap_procurement_move_rel(cr)
