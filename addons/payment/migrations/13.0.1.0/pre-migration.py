# Copyright 2020 Payam Yasaie <https://www.tashilgostar.com>
# Copyright 2020 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade
from psycopg2 import sql

_tables_rename = [
    ("account_invoice_transaction_rel", "openupgrade_legacy_13_0_ait_rel")
]

_column_renames = {
    'payment_acquirer': [('website_published', None)],
}

_column_copies = {
    'payment_acquirer': [('environment', None, None)],  # Preserve source value
}

_field_renames = [
    ('payment.acquirer', 'payment_acquirer', 'image_medium', 'image_128'),
    ('payment.acquirer', 'payment_acquirer', 'environment', 'state'),
]

_xmlid_renames = [
    ('payment.payment_acquirer_ogone', 'payment.payment_acquirer_ingenico'),
]


def map_payment_acquirer_state(cr):
    """ Adapt payment acquirer states to new definition.

    Done here for avoiding possible errors due to invalid state value when
    updating records.
    """
    openupgrade.logged_query(
        cr,
        sql.SQL(
            """UPDATE payment_acquirer
            SET state = CASE WHEN {} THEN 'enabled' ELSE 'disabled' END
            WHERE {} = 'prod'"""
        ).format(
            sql.Identifier(openupgrade.get_legacy_name('website_published')),
            sql.Identifier(openupgrade.get_legacy_name('environment'))
        )
    )


@openupgrade.migrate(use_env=True)
def migrate(env, version):
    openupgrade.copy_columns(env.cr, _column_copies)
    openupgrade.rename_tables(env.cr, _tables_rename)
    openupgrade.rename_fields(env, _field_renames)
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
    map_payment_acquirer_state(env.cr)
