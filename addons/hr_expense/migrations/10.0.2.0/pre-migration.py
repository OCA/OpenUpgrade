# -*- coding: utf-8 -*-
# Copyright 2017 Le Filament (<https://le-filament.com>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade


# Preserve columns which were moved to hr_expense_sheet in order to make the post migration
column_copies = {
    'hr_expense': [
        ('account_move_id', None, None),
        ('bank_journal_id', None, None),
        ('department_id', None, None),
        ('journal_id', None, None),
    ],
}



@openupgrade.migrate()
def migrate(env, version):
    openupgrade.copy_columns(env.cr, column_copies)
