# Copyright 2020 Payam Yasaie <https://www.tashilgostar.com>
# Copyright 2020 ForgeFlow <https://www.forgeflow.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade

_column_renames = {
    'account_cashbox_line': [
        ('default_pos_id', None),
    ],
    'account_journal': [
        ('amount_authorized_diff', None),
    ],
    'pos_order': [
        ('account_move', None),
        ('invoice_id', None),
    ],
}

_field_renames = [
    ('pos.category', 'pos_category', 'image', 'image_128'),
]


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.rename_columns(env.cr, _column_renames)
    openupgrade.rename_fields(env, _field_renames)
    # Fix image of pos.category after renaming column to image_128
    openupgrade.logged_query(
        env.cr, """
        UPDATE ir_attachment
        SET res_field = 'image_128'
        WHERE res_field = 'image_medium' and res_model = 'pos.category'
        """,
    )
