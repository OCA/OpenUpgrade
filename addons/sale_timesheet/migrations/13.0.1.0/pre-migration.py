# Copyright 2020 ForgeFlow S.L. (https://www.forgeflow.com)
# Copyright 2020 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade

_column_copies = {
    'product_template': [
        ('service_tracking', None, None),
    ],
}
_column_renames = {
    'account_analytic_line': [
        ('timesheet_invoice_id', None),
    ],
}


@openupgrade.migrate()
def migrate(env, version):
    cr = env.cr
    openupgrade.copy_columns(cr, _column_copies)
    openupgrade.rename_columns(cr, _column_renames)
