from openupgradelib import openupgrade


def _create_account_payment_method_line(env):
    # Populate account payment method lines from account payment methods
    # of code = 'check_printing' in order to enable functionally
    # this payment methods in the new logic
    # see https://github.com/odoo/odoo/blob/d039e762f1ccbbac6bc4e5f39cc70ed686d9281c/
    # addons/account_check_printing/models/account_journal.py#L81
    openupgrade.logged_query(
        env.cr,
        """
        INSERT INTO account_payment_method_line (name, sequence,
            payment_method_id, journal_id, create_uid, write_uid,
            create_date, write_date)
        SELECT apm.name, 10, apm.id, aj.id,
            apm.create_uid, apm.write_uid, apm.create_date, apm.write_date
        FROM account_payment_method apm
        JOIN account_journal aj ON aj.type = 'bank'
        WHERE apm.code = 'check_printing'
        """,
    )


@openupgrade.migrate()
def migrate(env, version):
    _create_account_payment_method_line(env)
