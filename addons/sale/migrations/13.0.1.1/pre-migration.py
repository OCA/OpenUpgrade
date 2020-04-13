# Copyright 2020 Payam Yasaie <https://www.tashilgostar.com>
# Copyright 2020 ForgeFlow <http://www.forgeflow.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade

_field_renames = [
    ('product.attribute', 'product_attribute',
     'type', 'display_type'),
    ('sale.order', 'sale_order',
     'confirmation_date', 'signed_on'),
]

column_renames = {
    'product_attribute_custom_value': [
        ('attribute_value_id', None),
    ],
}

_xmlid_renames = [
    # ir.model.access
    ('sale.access_account_invoice_manager', 'sale.access_account_move_manager'),
    ('sale.access_account_invoice_salesman', 'sale.access_account_move_salesman'),
]


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.rename_fields(env, _field_renames)
    openupgrade.rename_columns(env.cr, column_renames)
    openupgrade.rename_xmlids(env.cr, _xmlid_renames)
