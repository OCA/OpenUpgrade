from openupgradelib import openupgrade


def create_account_payment_method_line(env):
    """
    Create account payment method lines from account payment methods

    This is placed in 'end-' instead of 'post-' because we need to wait for
    other modules to update. For instance payment_adyen creates its
    'account.payment.method' object in XML and that is execute after this
    module has been migrated. But running this at 'end-' means that we will
    have that updated data.
    """
    openupgrade.logged_query(
        env.cr,
        """
        INSERT INTO account_payment_method_line (name, sequence,
            payment_method_id, journal_id, create_uid, write_uid,
            create_date, write_date)
        SELECT DISTINCT ON (apm.id, aj.id) apm.name, 10, apm.id, aj.id,
            apm.create_uid, apm.write_uid, apm.create_date, apm.write_date
        FROM account_payment_method apm
        JOIN payment_acquirer pa ON pa.provider = apm.code
        JOIN account_journal aj ON aj.type = 'bank' AND aj.id = pa.journal_id
        WHERE apm.code NOT IN ('manual', 'check_printing')
        """,
    )


@openupgrade.migrate()
def migrate(env, version):
    create_account_payment_method_line(env)
