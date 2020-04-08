# Copyright 2020 Payam Yasaie <https://www.tashilgostar.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade

_column_copies = {
    'account_invoice_transaction_rel': [
        ('invoice_id', None, None),
    ],

}

_column_renames = {
    'payment_acquirer': [
        ('website_published', None),
    ],

}

_field_renames = [
    ('payment.acquirer', 'payment_acquirer', 'image_medium', 'image_128'),
    ('payment.acquirer', 'payment_acquirer', 'environment', 'state'),
]

_xmlid_renames = [
    ('payment.payment_acquirer_ogone', 'payment.payment_acquirer_ingenico'),
]


@openupgrade.migrate(use_env=True)
def migrate(env, version):
    openupgrade.rename_fields(env, _field_renames)
    openupgrade.copy_columns(env.cr, _column_copies)
    openupgrade.rename_columns(env.cr, _column_renames)
    openupgrade.rename_xmlids(env.cr, _xmlid_renames)
    # Fix image of payment.acquirer after renaming column to image_128
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE ir_attachment
        SET res_field = 'image_128'
        WHERE res_field = 'image_medium' and res_model = 'payment.acquirer'
        """,
    )
