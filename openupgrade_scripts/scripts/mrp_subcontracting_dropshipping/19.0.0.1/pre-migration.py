# Copyright 2026 Heliconia Solutions Pvt. Ltd.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from openupgradelib import openupgrade

column_renames = {
    "stock_warehouse": [
        ("subcontracting_dropshipping_to_resupply", None),
    ],
}


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.rename_columns(env.cr, column_renames)
