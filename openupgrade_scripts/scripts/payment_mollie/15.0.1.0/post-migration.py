from openupgradelib import openupgrade


def _create_account_payment_method_line(env):
    # Create account payment method lines from account payment methods
    openupgrade.logged_query(
        env.cr,
        """
        INSERT INTO account_payment_method_line
        (name, payment_method_id, journal_id)
        SELECT apm.name, apm.id, aj.id
        FROM account_payment_method apm
        JOIN payment_acquirer pa ON pa.provider = 'mollie'
        JOIN account_journal aj ON aj.type = 'bank' AND aj.id = pa.journal_id
        WHERE apm.code = 'mollie'
        """,
    )


@openupgrade.migrate()
def migrate(env, version):
    _create_account_payment_method_line(env)
