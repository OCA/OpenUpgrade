# -*- coding: utf-8 -*-
# Copyright 2017 bloopark systems (<http://bloopark.de>)
# Copyright 2017 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade


# backup of separator column in table sale_layout_category because it doesn't
# exist anymore in odoo 10
column_renames_sale_layout = {
    'sale_layout_category': [
        ('separator', None),
    ],
}

field_renames_sale_layout = [
    ('account.invoice.line', 'account_invoice_line', 'sale_layout_cat_id',
     'layout_category_id'),
    ('account.invoice.line', 'account_invoice_line', 'categ_sequence',
     'layout_category_sequence'),
    ('sale.order.line', 'sale_order_line', 'sale_layout_cat_id',
     'layout_category_id'),
    ('sale.order.line', 'sale_order_line', 'categ_sequence',
     'layout_category_sequence'),
]


# rename_tables is not needed because "sale_layout.category" and
# "sale.layout_category" result both in "sale_layout_category"
model_renames_sale_layout = [
    ('sale_layout.category', 'sale.layout_category')
]


# backup of invoice_policy column with old / non existing value 'cost'
column_copies = {
    'product_template': [
        ('invoice_policy', None, None),
    ],
}


def migrate_sale_layout(env):
    # We need to manually removed these views because the cleanup is done
    # after YAML demo data is loaded and there's an error on that phase
    env.cr.execute(
        """
        DELETE FROM ir_ui_view
        WHERE NAME in %s
        """, (
            tuple([
                'sale.order.form.inherit_1',
                'account.invoice.form.inherit_1',
                'account.invoice.line.form.inherit_2',
            ]),
        )
    )
    if openupgrade.is_module_installed(env.cr, 'sale_layout'):
        openupgrade.rename_columns(env.cr, column_renames_sale_layout)
        openupgrade.rename_fields(env, field_renames_sale_layout)
        openupgrade.rename_models(env.cr, model_renames_sale_layout)


def cleanup_modules(cr):
    openupgrade.update_module_names(
        cr,
        [
            ('sale_layout', 'sale'),
            ('product_visible_discount', 'sale'),
        ],
        merge_modules=True
    )


def warning_update_module_names_partial(cr):
    """We don't use openupgrade.update_module_names here because only the
    fields sale_line_warn, sale_line_warn_msg, sale_warn and sale_warn_msg are
    moved from the old warning module to the sale module. Other fields are
    moved in other modules (e. g. field purchase_warn in purchase module). If
    we would using openupgrade.update_module_names there might be problems when
    first use openupgrade.update_module_names in sale module and then again in
    purchase module and so on.
    Because the field names didn't change and we only deal with text fields
    without constraints etc. we only have to change the related
    ir_model_data and ir_translation entries.
    """
    new_name = 'sale'
    old_name = 'warning'
    if not openupgrade.is_module_installed(cr, old_name):
        return

    # get moved model fields
    moved_fields = tuple(['sale_line_warn', 'sale_line_warn_msg',
                          'sale_warn', 'sale_warn_msg'])
    cr.execute("""
        SELECT id
        FROM ir_model_fields
        WHERE model IN ('res.partner', 'product.template') AND name in %s
    """, (moved_fields,))
    field_ids = tuple([r[0] for r in cr.fetchall()])

    # update ir_model_data, the subselect allows to avoid duplicated XML-IDs
    query = ("UPDATE ir_model_data SET module = %s "
             "WHERE module = %s AND res_id IN %s AND name NOT IN "
             "(SELECT name FROM ir_model_data WHERE module = %s)")
    openupgrade.logged_query(cr, query, (new_name, old_name, field_ids,
                                         new_name))

    # update ir_translation
    query = ("UPDATE ir_translation SET module = %s "
             "WHERE module = %s AND res_id IN %s")
    openupgrade.logged_query(cr, query, (new_name, old_name, field_ids))


def sale_expense_update_module_names_partial(cr):
    """We don't use openupgrade.update_module_names here because the field
    expense_policy is moved from the sale_expense module to the sale module but
    sale_expense still exists in odoo 10.
    Because the field name didn't change and we only deal with text field
    without constraints etc. we only have to change the related ir_model_data
    entries.
    """
    new_name = 'sale'
    old_name = 'sale_expense'
    if not openupgrade.is_module_installed(cr, old_name):
        return

    # get moved model fields
    moved_fields = tuple(['expense_policy'])
    cr.execute("""
        SELECT id
        FROM ir_model_fields
        WHERE model = 'product.template' AND name in %s
    """, (moved_fields,))
    field_ids = tuple([r[0] for r in cr.fetchall()])

    # update ir_model_data, the subselect allows to avoid duplicated XML-IDs,
    query = ("UPDATE ir_model_data SET module = %s "
             "WHERE module = %s AND res_id IN %s AND name NOT IN "
             "(SELECT name FROM ir_model_data WHERE module = %s)")
    openupgrade.logged_query(cr, query, (new_name, old_name, field_ids,
                                         new_name))

    # delete ir_translation because the translations changes completely
    query = ("DELETE FROM ir_translation "
             "WHERE module = %s AND res_id IN %s")
    openupgrade.logged_query(cr, query, (old_name, field_ids))


def migrate_account_invoice_shipping_address(env):
    """The feature of this module is now on core, so we merge and change data
    accordingly.
    """
    cr = env.cr
    module_name = 'account_invoice_shipping_address'
    if not openupgrade.is_module_installed(cr, module_name):
        return
    openupgrade.update_module_names(
        cr, [(module_name, 'sale')], merge_modules=True,
    )
    openupgrade.rename_fields(env, [
        ('account.invoice', 'account_invoice', 'address_shipping_id',
         'partner_shipping_id')
    ])


@openupgrade.migrate(use_env=True)
def migrate(env, version):
    migrate_sale_layout(env)
    openupgrade.copy_columns(env.cr, column_copies)
    cleanup_modules(env.cr)
    warning_update_module_names_partial(env.cr)
    sale_expense_update_module_names_partial(env.cr)
    migrate_account_invoice_shipping_address(env)
