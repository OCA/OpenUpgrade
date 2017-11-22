# -*- coding: utf-8 -*-
# Copyright 2017 Tecnativa - Vicent Cubells
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade

column_copies = {
    'hr_expense': [
        ('state', None, None),
    ]
}


@openupgrade.migrate(use_env=True)
def migrate(env, version):
    openupgrade.copy_columns(env.cr, column_copies)
    record = env.ref('hr_expense.action_client_expense_menu', False)
    if record:
        record.unlink()
