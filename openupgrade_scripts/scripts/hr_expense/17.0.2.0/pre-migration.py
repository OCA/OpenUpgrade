# Copyright 2024 Viindoo Technology Joint Stock Company (Viindoo)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade

_fields_renames = [
    (
        "hr.expense",
        "hr_expense",
        "amount_tax",
        "tax_amount_currency",
    ),
    (
        "hr.expense",
        "hr_expense",
        "amount_tax_company",
        "tax_amount",
    ),
    (
        "hr.expense",
        "hr_expense",
        "price_unit",
        "unit_price",
    ),
    (
        "hr.expense",
        "hr_expense",
        "untaxed_amount",
        "untaxed_amount_currency",
    ),
    (
        "hr.expense",
        "hr_expense",
        "total_amount",
        "total_amount_currency",
    ),
    (
        "hr.expense",
        "hr_expense",
        "total_amount_company",
        "total_amount",
    ),
    (
        "hr.expense.sheet",
        "hr_expense_sheet",
        "total_amount_taxes",
        "total_tax_amount",
    ),
]


def _am_update_expense_sheet_id(env):
    openupgrade.logged_query(
        env.cr,
        """
        ALTER TABLE account_move
        ADD COLUMN IF NOT EXISTS expense_sheet_id INTEGER
        """,
    )
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE account_move am
        SET expense_sheet_id = sheet.id
        FROM hr_expense_sheet sheet
        WHERE am.id = sheet.account_move_id
        """,
    )


def _hr_expense_update_state(env):
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE hr_expense expense
        SET state = 'reported'
        FROM hr_expense_sheet sheet
        WHERE expense.sheet_id = sheet.id AND
        sheet.state = 'draft'
        """,
    )


def _hr_expense_sheet_fill_approval_state(env):
    openupgrade.logged_query(
        env.cr,
        """
        ALTER TABLE hr_expense_sheet
        ADD COLUMN IF NOT EXISTS approval_state VARCHAR
        """,
    )
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE hr_expense_sheet
        SET approval_state = CASE
            WHEN state = 'submit' then 'submit'
            WHEN state in ('approve', 'post', 'done') then 'approve'
            WHEN state = 'cancel' then 'cancel'
        END
        """,
    )


def _hr_expense_sheet_journal(env):
    openupgrade.logged_query(
        env.cr,
        """
        ALTER TABLE hr_expense_sheet
            ADD COLUMN IF NOT EXISTS employee_journal_id INTEGER,
            ADD COLUMN IF NOT EXISTS payment_method_line_id INTEGER;
        """,
    )
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE hr_expense_sheet sheet
        SET payment_method_line_id = method_line.id
        FROM account_journal journal
            JOIN account_payment_method_line method_line
                ON method_line.journal_id = journal.id
            JOIN account_payment_method method
                ON method.id = method_line.payment_method_id
        WHERE sheet.bank_journal_id = journal.id
        AND method.payment_type = 'outbound'
        """,
    )
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE hr_expense_sheet
        SET employee_journal_id = journal_id
        WHERE journal_id IS NOT NULL
        """,
    )
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE hr_expense_sheet sheet
        SET journal_id = CASE
        WHEN bank_journal_id IS NOT NULL
        AND expense.payment_mode = 'company_account' THEN bank_journal_id
        FROM hr_expense expense
        WHERE expense.sheet_id = sheet.id
        """,
    )


@openupgrade.migrate()
def migrate(env, version):
    _am_update_expense_sheet_id(env)
    openupgrade.rename_fields(env, _fields_renames)
    _hr_expense_update_state(env)
    _hr_expense_sheet_fill_approval_state(env)
