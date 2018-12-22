# Copyright 2018 Eficent <http://www.eficent.com>
# Copyright 2018 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade

column_copies = {
    'account_analytic_line': [
        ('company_id', None, None),
    ],
}


@openupgrade.migrate(use_env=False)
def migrate(cr, version):
    openupgrade.copy_columns(cr, column_copies)
