from openupgradelib import openupgrade


def _fill_payment_state(env):
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE hr_expense_sheet
        SET payment_state = 'not_paid'
        WHERE account_move_id IS NULL
        """,
    )
    # Recompute payment_state for the moves associated to the expenses, as on
    # v14 these ones were not computed being of type `entry`, which changes now
    # on v15 if the method `_payment_state_matters` returns True, which is the
    # case for the expense moves
    # Disable the reconciliation check to be able to update reconciled moves
    _check_reconciliation = env["account.move.line"].__class__._check_reconciliation
    _check_fiscalyear_lock_date = env[
        "account.move"
    ].__class__._check_fiscalyear_lock_date
    env["account.move.line"].__class__._check_reconciliation = lambda self: None
    env["account.move"].__class__._check_fiscalyear_lock_date = lambda self: None
    env["hr.expense.sheet"].search([]).account_move_id._compute_amount()
    env["account.move.line"].__class__._check_reconciliation = _check_reconciliation
    env[
        "account.move"
    ].__class__._check_fiscalyear_lock_date = _check_fiscalyear_lock_date
    # Now perform the SQL to transfer the payment_state
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE hr_expense_sheet hes
        SET payment_state = am.payment_state
        FROM account_move am
        WHERE am.id = hes.account_move_id
        """,
    )


@openupgrade.migrate()
def migrate(env, version):
    _fill_payment_state(env)
    openupgrade.load_data(env.cr, "hr_expense", "15.0.2.0/noupdate_changes.xml")
    openupgrade.delete_record_translations(
        env.cr, "hr_expense", ["hr_expense_template_register"]
    )
