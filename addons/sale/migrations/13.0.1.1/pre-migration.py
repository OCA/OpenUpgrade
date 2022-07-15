# Copyright 2020 Payam Yasaie <https://www.tashilgostar.com>
# Copyright 2020 ForgeFlow <http://www.forgeflow.com>
# Copyright 2020 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade

_table_renames = [
    ("sale_order_line_invoice_rel", "ou_sale_order_line_invoice_rel"),
]

_field_renames = [
    ('product.attribute', 'product_attribute',
     'type', 'display_type'),
    ('product.template', 'product_template',
     'hide_expense_policy', 'visible_expense_policy'),
    ('product.product', 'product_product',
     'hide_expense_policy', 'visible_expense_policy'),
]

_column_renames = {
    'product_attribute_custom_value': [
        ('attribute_value_id', None),
    ],
}

_column_copies = {
    "sale_order": [("date_order", None, None)],
}

_xmlid_renames = [
    # ir.model.access
    ('sale.access_account_invoice_manager', 'sale.access_account_move_manager'),
    ('sale.access_account_invoice_salesman', 'sale.access_account_move_salesman'),
]


def nullify_invoiced_target_when_not_used(env):
    """If `use_invoices` was not checked in previous version, the invoice target
    was not evaluated, no matter the value. But now in v13, there's no check,
    and the target is evaluated if distinct from 0, so we need to nullify this
    target for not checked teams.
    """
    openupgrade.logged_query(
        env.cr,
        "UPDATE crm_team SET invoiced_target = 0 WHERE NOT use_invoices",
    )


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.rename_tables(env.cr, _table_renames)
    openupgrade.rename_fields(env, _field_renames)
    openupgrade.rename_columns(env.cr, _column_renames)
    openupgrade.copy_columns(env.cr, _column_copies)
    openupgrade.rename_xmlids(env.cr, _xmlid_renames)
    openupgrade.update_module_moved_fields(
        env.cr, "sale.order", ["campaign_id", "medium_id", "source_id"], "sale_crm", "sale"
    )
    openupgrade.add_fields(
        env, [("company_id", "utm.campaign", False, "many2one", False, "sale")],
    )
    nullify_invoiced_target_when_not_used(env)
