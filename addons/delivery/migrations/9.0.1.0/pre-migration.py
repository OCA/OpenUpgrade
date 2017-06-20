# -*- coding: utf-8 -*-
# © 2016 Therp BV <http://therp.nl>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade

column_renames = {
    'delivery_grid_line': [
        ('type', 'variable'),
    ],
}

column_copies = {
    'delivery_grid_line': [
        ('list_price', 'list_base_price', None),
    ],
}

table_renames = [
    ('delivery_grid_line', 'delivery_price_rule'),
]


@openupgrade.migrate()
def migrate(cr, version):
    openupgrade.rename_columns(cr, column_renames)
    openupgrade.copy_columns(cr, column_copies)
    openupgrade.rename_tables(cr, table_renames)
