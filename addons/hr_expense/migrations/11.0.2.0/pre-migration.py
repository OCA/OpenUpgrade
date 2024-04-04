# -*- coding: utf-8 -*-
# Copyright 2024 ForgeFlow (<https://www.forgeflow.com>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade

_table_renames = [
    ('hr_expense_register_payment_wizard', 'hr_expense_sheet_register_payment_wizard')
]

_model_renames = [
    ('hr.expense.register.payment.wizard', 'hr.expense.sheet.register.payment.wizard')
]


@openupgrade.migrate(use_env=True)
def migrate(env, version):
    openupgrade.rename_tables(env.cr, _table_renames)
    openupgrade.rename_models(env.cr, _model_renames)
