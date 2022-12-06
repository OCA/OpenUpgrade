from openupgradelib import openupgrade


def _fast_fill_account_payment_outstanding_account_id(env):
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE account_payment ap
        SET outstanding_account_id = apml.payment_account_id
        FROM account_payment_method_line apml
        WHERE apml.id = ap.payment_method_line_id
            AND ap.payment_type IN ('inbound', 'outbound')""",
    )
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE account_payment ap
        SET outstanding_account_id =
            CASE
                WHEN ap.payment_type = 'inbound'
                THEN COALESCE(aj.payment_debit_account_id,
                    c.account_journal_payment_debit_account_id)
                WHEN ap.payment_type = 'outbound'
                THEN COALESCE(aj.payment_credit_account_id,
                    c.account_journal_payment_credit_account_id)
            END
        FROM account_move am
        JOIN account_journal aj ON am.journal_id = aj.id
        JOIN res_company c ON c.id = aj.company_id
        WHERE ap.move_id = am.id
            AND ap.payment_type IN ('inbound', 'outbound')
            AND ap.outstanding_account_id IS NULL""",
    )


@openupgrade.migrate()
def migrate(env, version):
    _fast_fill_account_payment_outstanding_account_id(env)
