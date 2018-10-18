# Copyright 2018 Eficent <http://www.eficent.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade

_column_renames = {
    'res_partner': [
        ('opt_out', None),
    ],
}

_field_renames = [
    ('mail.activity.type', 'mail_activity_type', 'days', 'delay_count'),
]


@openupgrade.migrate(use_env=True)
def migrate(env, version):
    cr = env.cr
    openupgrade.rename_columns(cr, _column_renames)
    openupgrade.rename_fields(env, _field_renames)
