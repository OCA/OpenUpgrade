# -*- coding: utf-8 -*-
# © 2017 Therp BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade


@openupgrade.migrate(use_env=True)
def migrate(env, version):
    cr = env.cr
    # copy columns good practice in pre-mig script format of colum_spec should
    # be: { Table_name_in_db : [( old_column_name , new_column_name, type)]
    # defaults of new columname are fetchable via method get_legacy_name
    openupgrade.copy_columns(
        cr, {
            'account_analytic_account': [
                ('account_type', None, None),
            ],
        })
