# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Alexandre Fayolle
#    Copyright 2014 Camptocamp SA
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
    # Using magic None value to trigger call to get_legacy_name()
    'product_supplierinfo': [
        ('product_id', None),
        ],
    'product_product': [
        ('color', None),
        ('image', 'image_variant'),
        ],
    'product_template': [
        ('produce_delay', None), # need to handle in mrp migration
        ('cost_method', None),  # need to handle in stock_account migration
        ],
    'product_packaging': [
        ('height', None),
        ('length', None),
        ('weight_ul', None),
        ('width', None),
        ]
        }


@openupgrade.migrate()
def migrate(cr, version):
    openupgrade.rename_columns(cr, column_renames)
