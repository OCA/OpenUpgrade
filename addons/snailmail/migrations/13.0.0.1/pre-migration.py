# Copyright 2020 ForgeFlow <http://www.forgeflow.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade

_column_copies = {
    'snailmail_letter': [
        ('state', None, None),
    ],
}


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.copy_columns(env.cr, _column_copies)
