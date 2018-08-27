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


def fix_act_window(env):
    """Action window with XML-ID 'stock.action_procurement_compute' has
    set src_model='procurement.order' in v8, but in v9 it doesn't have
    src_model. So to avoid possible errors in future migrations, we empty
    that value before that happens.
    """
    openupgrade.logged_query(
        env.cr, """
        UPDATE ir_act_window iaw
        SET src_model = NULL
        FROM ir_model_data imd
        WHERE imd.res_id = iaw.id
            AND imd.module = 'stock'
            AND imd.name = 'action_procurement_compute'""",
    )


@openupgrade.migrate(use_env=True)
def migrate(env, version):
    cr = env.cr
    openupgrade.rename_xmlids(cr, xmlids)
    openupgrade.rename_columns(cr, column_renames)
    openupgrade.rename_fields(env, field_renames)
    fix_act_window(env)
