from openupgradelib import openupgrade


def _compute_payment_state(env):
    openupgrade.logged_query(
        env.cr,
        """
        ALTER TABLE hr_expense_sheet
        ADD COLUMN IF NOT EXISTS payment_state varchar
        """,
    )
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE hr_expense_sheet
        SET payment_state = 'not_paid'
        WHERE account_move_id IS NULL
        """,
    )
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE hr_expense_sheet expense_sheet
        SET payment_state = CASE
            WHEN am.payment_state IS NOT NULL THEN am.payment_state
            ELSE 'not_paid'
            END
        FROM account_move am
        WHERE
            expense_sheet.account_move_id IS NOT NULL
            AND am.id = expense_sheet.account_move_id
        """,
    )


def _compute_currency_id_has_not_value(env):
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE hr_expense e
        SET currency_id = c.currency_id
        FROM res_company c
        WHERE e.currency_id IS NULL AND c.id = e.company_id
        """,
    )


@openupgrade.migrate()
def migrate(env, version):
    _compute_currency_id_has_not_value(env)
    _compute_payment_state(env)
