# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: ONESTEiN B.V.
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

from openerp.openupgrade import openupgrade

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
    ('stock.property_stock_account_input_categ', 'stock_account.property_stock_account_input_categ'),
    ('stock.property_stock_account_input_prd', 'stock_account.property_stock_account_input_prd'),
    ('stock.property_stock_account_output_categ', 'stock_account.property_stock_account_output_categ'),
    ('stock.property_stock_account_output_prd', 'stock_account.property_stock_account_output_prd'),
    ('stock.property_stock_journal', 'stock_account.property_stock_journal'),
    ('stock.stock_journal', 'stock_account.stock_journal'),
]


def save_rel_table(cr):
    simr_legacy = openupgrade.get_legacy_name('stock_inventory_move_rel')
    openupgrade.logged_query(cr, """CREATE TABLE {} AS TABLE stock_inventory_move_rel""".format(simr_legacy))


def initialize_location_inventory(cr):
    """Stock Inventory is upgraded before Stock Warehouse. The default value of the field location_id is searched
    in the stock_warehouse table, asking for columns that has not been created yet because of the browse object.
    So the query fails.

    This function is a proposal to solve this problem. It creates and assigns this field like the ORM does before
    the regular upgrade mechanism of Odoo.
    :param cr: Database cursor
    """

    cr.execute("""SELECT res_id FROM ir_model_data WHERE name = %s""", ('stock_location_stock',))
    default_location = cr.fetchone()
    default_location = default_location and default_location[0] or False

    cr.execute("""ALTER TABLE stock_inventory ADD COLUMN location_id INTEGER NOT NULL DEFAULT %s""",
               (default_location,))
    cr.execute("""COMMENT ON COLUMN stock_inventory.location_id IS %s""", ('Inventoried Location',))


@openupgrade.migrate()
def migrate(cr, version):
    openupgrade.rename_columns(cr, column_renames)
    openupgrade.rename_xmlids(cr, xmlid_renames)
    initialize_location_inventory(cr)
    save_rel_table(cr)
