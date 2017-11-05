# -*- coding: utf-8 -*-
# Copyright 2014 Microcom, Therp BV
# Copyright 2017 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade

xmlids = [
    ('stock.view_partner_property_form', 'stock.view_partner_stock_form'),
]

column_renames = {
    'product_template': [
        ('loc_case', None),
        ('loc_rack', None),
        ('loc_row', None)
    ],
    'stock_pack_operation': [
        ('cost', None),
        ('currency', None),
        ('lot_id', None),
        ('processed', None),
    ],
}

field_renames = [
    # renamings with oldname attribute - They also need the rest of operations
    ('stock.location', 'stock_location', 'loc_barcode', 'barcode'),
]


@openupgrade.migrate(use_env=True)
def migrate(env, version):
    cr = env.cr
    openupgrade.rename_xmlids(cr, xmlids)
    openupgrade.rename_columns(cr, column_renames)
    openupgrade.rename_fields(env, field_renames)
