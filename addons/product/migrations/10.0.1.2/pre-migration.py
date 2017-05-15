# -*- coding: utf-8 -*-
# © 2017 Therp BV <http://therp.nl>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade

_column_renames = {
    'product_attribute_value_product_product_rel': [
        ('prod_id', 'product_product_id'),
        ('att_id', 'product_attribute_value_id'),
    ],
    'product_attribute_line_product_attribute_value_rel': [
        ('line_id', 'product_attribute_line_id'),
        ('val_id', 'product_attribute_value_id'),
    ],
    # Preserve fields just in case that someone uses them in other modules.
    'product_category': [
        ('sequence', None),
    ],
    'product_template': [
        ('state', None),
        ('product_manager', None)
    ],
}


@openupgrade.migrate(use_env=False)
def migrate(cr, version):
    openupgrade.rename_columns(cr, _column_renames)
