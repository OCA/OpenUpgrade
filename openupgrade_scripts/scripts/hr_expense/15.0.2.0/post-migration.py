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
        UPDATE account_move_line
        SET exclude_from_invoice_tab=(coalesce(quantity, 0) = 0)
        WHERE expense_id IS NOT NULL
        """,
    )
    # Recompute payment_state for the moves associated to the expenses, as on
    # v14 these ones were not computed being of type `entry`, which changes now
    # on v15 if the method `_payment_state_matters` returns True, which is the
    # case for the expense moves
    for move in env["hr.expense.sheet"].search([]).account_move_id:
        # Extracted and adapted from _compute_amount() in account.move
        new_pmt_state = "not_paid" if move.move_type != "entry" else False
        total_to_pay = total_residual = 0.0
        for line in move.line_ids:
            if line.account_id.user_type_id.type in ("receivable", "payable"):
                total_to_pay += line.balance
                total_residual += line.amount_residual
        currencies = move._get_lines_onchange_currency().currency_id
        currency = currencies if len(currencies) == 1 else move.company_id.currency_id
        if currency.is_zero(move.amount_residual):
            reconciled_payments = move._get_reconciled_payments()
            if not reconciled_payments or all(
                payment.is_matched for payment in reconciled_payments
            ):
                new_pmt_state = "paid"
            else:
                new_pmt_state = move._get_invoice_in_payment_state()
        elif currency.compare_amounts(total_to_pay, total_residual) != 0:
            new_pmt_state = "partial"
        move.payment_state = new_pmt_state


@openupgrade.migrate()
def migrate(env, version):
    _fill_payment_state(env)
    openupgrade.load_data(env.cr, "hr_expense", "15.0.2.0/noupdate_changes.xml")
    openupgrade.delete_record_translations(
        env.cr, "hr_expense", ["hr_expense_template_register"]
    )
