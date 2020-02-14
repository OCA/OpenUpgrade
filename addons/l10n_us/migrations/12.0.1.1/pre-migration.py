# Copyright 2020 ForgeFLow <http://www.forgeflow.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade

_column_renames = {
    'res_partner_bank': [
        ('aba_routing', None),
    ],
}


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.rename_columns(env.cr, _column_renames)
