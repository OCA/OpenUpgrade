# Copyright 2026 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from openupgradelib import openupgrade


def _set_hr_expense_state(env):
    """Recompute hr.expense#state for records in states 'done', 'reported'.

    Done here because `_get_invoice_in_payment_state` should return the proper state.
    """
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE hr_expense
        SET state = COALESCE(approval_state, 'draft')
        WHERE account_move_id IS NULL
            AND state IN ('done', 'reported')
        """,
    )
    in_payment_state = env["account.move"]._get_invoice_in_payment_state()
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE hr_expense he
        SET state = CASE
            WHEN he.payment_mode = 'company_account' THEN 'paid'
            WHEN am.state = 'draft' OR am.payment_state = 'not_paid' THEN 'posted'
            WHEN am.payment_state = 'in_payment'
                OR (
                    am.payment_state = 'partial'
                    AND ROUND(am.amount_residual, 0) != 0
                ) THEN %s
        ELSE 'paid'
        END
        FROM account_move am
        WHERE he.account_move_id = am.id
            AND he.state IN ('done', 'approved', 'reported')
        """,
        (in_payment_state,),
    )


@openupgrade.migrate()
def migrate(env, version):
    _set_hr_expense_state(env)
