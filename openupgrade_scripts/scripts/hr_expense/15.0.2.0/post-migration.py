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
    # set exclude_from_invoice_tab the way v15 does it
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE account_move_line AS aml
        SET exclude_from_invoice_tab = true
        FROM
            account_account AS aa,
            account_account_type AS aat
        WHERE
            aml.account_id = aa.id AND
            aa.user_type_id = aat.id AND
            aml.expense_id IS NOT NULL AND
            aat.type = 'payable'
        """,
    )
    # Disable fiscalyear_lock_date check
    _check_fiscalyear_lock_date = env[
        "account.move"
    ].__class__._check_fiscalyear_lock_date
    env["account.move"].__class__._check_fiscalyear_lock_date = lambda self: None
    # Recompute several fields (always_tax_exigible, amount_residual,
    # amount_residual_signed, amount_untaxed, amount_untaxed_signed,
    # payment_state) for the moves associated to the expenses, as on v14 these
    # ones were not computed being of type `entry`, which changes now on v15
    # if the method `_payment_state_matters` returns True, which is the case
    # for the expense moves
    env["account.move"].with_context(active_test=False, tracking_disable=True).search(
        [("line_ids.expense_id", "!=", False)]
    )._compute_amount()
    # Enable fiscalyear_lock_date check
    env[
        "account.move"
    ].__class__._check_fiscalyear_lock_date = _check_fiscalyear_lock_date


@openupgrade.migrate()
def migrate(env, version):
    _fill_payment_state(env)
    openupgrade.load_data(env.cr, "hr_expense", "15.0.2.0/noupdate_changes.xml")
    openupgrade.delete_record_translations(
        env.cr, "hr_expense", ["hr_expense_template_register"]
    )
