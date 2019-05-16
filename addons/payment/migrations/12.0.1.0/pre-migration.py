# Copyright 2018 Eficent <http://www.eficent.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade

column_copies = {
    'payment_transaction': [
        ('state', None, None),
    ],
}

_field_renames = [
    ('payment.transaction', 'payment_transaction', 'date_validate', 'date'),
]


@openupgrade.migrate(use_env=True)
def migrate(env, version):
    openupgrade.copy_columns(env.cr, column_copies)
    openupgrade.rename_fields(env, _field_renames)
