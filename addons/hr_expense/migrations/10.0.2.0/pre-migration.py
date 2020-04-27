# -*- coding: utf-8 -*-
# Copyright 2017 Tecnativa - Vicent Cubells
# Copyright 2020 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade

column_copies = {
    'hr_expense': [
        ('state', None, None),
    ]
}


def _detect_hr_expense_v8(env):
    """If you come from v8 and haven't cleaned up table, it's possible
    to rescue previous expense sheets and use them in this version.
    """
    _table = "openupgrade_legacy_9_0_hr_expense_expense"
    if not openupgrade.table_exists(env.cr, _table):
        return
    openupgrade.rename_models(
        env.cr, [('hr.expense.expense', 'hr.expense.sheet')])
    openupgrade.rename_tables(env.cr, [(_table, 'hr_expense_sheet')])
    openupgrade.rename_fields(env, [
        ('hr.expense.sheet', 'hr_expense_sheet', 'amount', 'total_amount'),
        ('hr.expense.sheet', 'hr_expense_sheet', 'user_id', 'responsible_id'),
        ('hr.expense', 'hr_expense', 'expense_id', 'sheet_id'),
    ])
    openupgrade.add_fields(env, [
        # For avoiding to be filled by default value
        ('bank_journal_id', 'hr.expense.sheet', 'hr_expense_sheet',
         'many2one', False, 'hr_expense'),
        ('accounting_date', 'hr.expense.sheet', 'hr_expense_sheet',
         'date', False, 'hr_expense'),
    ])
    openupgrade.logged_query(
        env.cr, """UPDATE hr_expense_sheet hes
        SET accounting_date = am.date
        FROM account_move am
        WHERE am.id = hes.account_move_id""",
    )
    openupgrade.map_values(
        env.cr, 'openupgrade_legacy_9_0_state', 'state', [
            ('draft', 'submit'),
            ('cancelled', 'cancel'),
            ('confirm', 'submit'),
            ('accepted', 'approve'),
            ('done', 'post'),
            ('paid', 'done'),
        ], table='hr_expense_sheet',
    )


@openupgrade.migrate(use_env=True)
def migrate(env, version):
    openupgrade.copy_columns(env.cr, column_copies)
    _detect_hr_expense_v8(env)
    record = env.ref('hr_expense.action_client_expense_menu', False)
    if record:
        record.unlink()
