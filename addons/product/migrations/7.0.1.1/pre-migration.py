# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    This migration script copyright (C) 2012-2013 Georges Abitbol
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

from openupgrade import openupgrade

column_renames = {
    'product_product': [
        ('product_image', 'image'),
    ]
}

xmlid_renames = [
    ('product.decimal_sale', 'product.decimal_price'), 
    ('product.cat0', 'product.product_category_all'), 
    ('product.product_consultant', 'product.product_product_consultant'), 
    ('product.uom_day', 'product.product_uom_day'), 
    ('product.uom_hour', 'product.product_uom_hour'), 
]

@openupgrade.migrate()
def migrate(cr, version):
    openupgrade.rename_columns(cr, column_renames)
    openupgrade.rename_xmlids(cr, xmlid_renames)
