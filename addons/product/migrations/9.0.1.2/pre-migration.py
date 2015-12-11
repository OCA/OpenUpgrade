# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenUpgrade module for Odoo
#    @copyright 2014-Today: Odoo Community Association, Microcom
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

from openupgradelib import openupgrade


# For 'base' map_values in post-migration
column_renames = {
    'product_pricelist_item': [
        ('base', None),
    ],
}

def convert_template_id_to_product_id(cr):
    openupgrade.logged_query(cr, """
        UPDATE product_price_history ph
        SET product_id = p.id
        FROM product_product p
        WHERE ph.product_template_id = p.id
        """)

@openupgrade.migrate()
def migrate(cr, version):
    openupgrade.logged_query(cr, """ALTER TABLE product_price_history
              ADD COLUMN product_id integer
              """)
    convert_template_id_to_product_id(cr)
    openupgrade.logged_query(cr, """
        ALTER TABLE product_pricelist_item
        ALTER COLUMN base
        TYPE VARCHAR
        """)
    # unsure if this xml rename is needed here, trying to resolve product_view.xml not loading when migrating
    openupgrade.rename_xmlids(cr, [('product.variants_template_tree_view', 'product.product_attribute_value_view_tree')])
