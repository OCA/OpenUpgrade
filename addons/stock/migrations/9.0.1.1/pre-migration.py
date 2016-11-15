# -*- coding: utf-8 -*-
# @copyright 2014-Today: Odoo Community Association, Microcom, Therp BV
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


@openupgrade.migrate()
def migrate(cr, version):
    openupgrade.rename_xmlids(cr, xmlids)
    openupgrade.rename_columns(cr, column_renames)
