# Copyright 2021 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade


_rename_columns = {
    "repair_fee": [('invoice_line_id', None)],
    "repair_line": [('invoice_line_id', None)],
    "repair_order": [('invoice_id', None)],
}


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.rename_columns(env.cr, _rename_columns)
