# Copyright 2020 ForgeFlow <http://www.forgeflow.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade

_column_copies = {
    'purchase_order_line': [
        ('qty_received', 'qty_received_manual', None),
    ],
}

_column_renames = {
    'purchase_order': [
        ('date_approve', None),
    ],
}

_xmlid_renames = [
    ("purchase.access_account_invoice_purchase",
     "purchase.access_account_move_purchase"),
    ("purchase.access_account_invoice_purchase_manager",
     "purchase.access_account_move_purchase_manager"),
]


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.copy_columns(env.cr, _column_copies)
    openupgrade.rename_columns(env.cr, _column_renames)
    openupgrade.rename_xmlids(env.cr, _xmlid_renames)
    openupgrade.logged_query(
        env.cr, """
        ALTER TABLE purchase_order_line
        ADD COLUMN qty_received_method varchar""",
    )
