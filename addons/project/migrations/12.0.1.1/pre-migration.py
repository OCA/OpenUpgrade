# Copyright 2019 Eficent <http://www.eficent.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade

column_copies = {
    'project_project': [
        ('analytic_account_id', None, None),
    ],
}


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.copy_columns(env.cr, column_copies)
