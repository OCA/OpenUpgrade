# -*- coding: utf-8 -*-
# Copyright 2017 Trescloud <http://trescloud.com>
# Copyright 2017 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade

column_copies = {
    'procurement_rule': [
        ('route_sequence', None, None),
    ],
    'stock_location_path': [
        ('auto', None, None),
        ('route_sequence', None, None),
    ],
}

field_renames = [
    # renamings with oldname attribute - They also need the rest of operations
    ('stock.pack.operation', 'stock_pack_operation', 'processed_boolean',
     'is_done'),
]

xmlid_renames = [
    ('stock.group_locations', 'stock.group_stock_multi_locations'),
]


def warning_update_module_names_partial(cr):
    """We don't use openupgrade.update_module_names here because only the
    fields picking_warn and picking_warn_msg are moved from the old warning
    module to the stock one. Other fields are moved in other modules (e. g.
    field purchase_warn in purchase module). If we would using
    openupgrade.update_module_names there might be problems when
    first use openupgrade.update_module_names in stock module and then again in
    purchase module and so on.
    Because the field names didn't change and we only deal with text fields
    without constraints etc. we only have to change the related
    ir_model_data and ir_translation entries.
    """
    new_name = 'stock'
    old_name = 'warning'
    if not openupgrade.is_module_installed(cr, old_name):
        return
    # get moved model fields
    moved_fields = [
        'picking_warn',
        'picking_warn_msg',
    ]
    cr.execute("""
        SELECT id
        FROM ir_model_fields
        WHERE model = 'res.partner' AND name in %s
        """, (tuple(moved_fields),))
    field_ids = [r[0] for r in cr.fetchall()]
    # update ir_model_data, the subselect allows to avoid duplicated XML-IDs
    query = ("UPDATE ir_model_data SET module = %s "
             "WHERE module = %s AND res_id IN %s AND name NOT IN "
             "(SELECT name FROM ir_model_data WHERE module = %s)")
    openupgrade.logged_query(cr, query, (new_name, old_name, tuple(field_ids),
                                         new_name))
    # update ir_translation
    query = ("UPDATE ir_translation SET module = %s "
             "WHERE module = %s AND res_id IN %s")
    openupgrade.logged_query(cr, query, (new_name, old_name, tuple(field_ids)))


@openupgrade.migrate(use_env=True)
def migrate(env, version):
    cr = env.cr
    openupgrade.copy_columns(cr, column_copies)
    openupgrade.float_to_integer(cr, 'procurement_rule', 'route_sequence')
    openupgrade.float_to_integer(cr, 'stock_location_path', 'route_sequence')
    openupgrade.rename_xmlids(env.cr, xmlid_renames)
    openupgrade.rename_fields(env, field_renames)
    warning_update_module_names_partial(cr)
