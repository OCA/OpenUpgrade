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
                  'product_category': [
                    ],
                  'product_product': [
                         ('track_incoming', None),
                         ('track_outgoing', None),
                         ('track_production', None),
                         ('valuation', None)
                    ],
                  'stock_warehouse_orderpoint': [
                         ('procurement_id', None),
                    ],
                  'product_template': [
                    ],
                  'stock_inventory': [
                         ('date_done', None),
                    ],
                  'stock_inventory_line': [
                            ('product_uom', 'product_uom_id'),
                    ],
                  'stock_move': [
                            ('auto_validate', None),
                    ],
                  'procurement_order' : [
                       ('procure_method' , None)
                 ]

        }

xmlid_renames = [
      ('procurement.sequence_mrp_op_type',
       'stock.sequence_mrp_op_type'),
    ]

def save_rel_table(cr):
    simr_legacy = openupgrade.get_legacy_name('stock_inventory_move_rel')
    openupgrade.logged_query(
        cr,
        """
    CREATE TABLE {} AS TABLE stock_inventory_move_rel
        """.format(simr_legacy))

@openupgrade.migrate()
def migrate(cr, version):
    openupgrade.rename_columns(cr, column_renames)
    openupgrade.rename_xmlids(cr, xmlid_renames)

    save_rel_table(cr)
