# -*- coding: utf-8 -*-
# © 2016 Therp BV <http://therp.nl>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade


def update_payments_from_vouchers(env):
    """Update account.payment rows from corresponding account.voucher rows."""
    # Use the fact that id of migrated account_payment is id of original
    # account_voucher.
    # Do not set: check_number = av.number
    # new check_number is integer value, av.number was text filled from
    # sequence.
    env.cr.execute(
        """\
        UPDATE account_payment ap
        SET
            check_amount_in_words = av.amount_in_word
        FROM account_voucher av
        WHERE ap.id = av.id
        """
    )
    check_method = env.ref(
        'account_check_printing.account_payment_method_check')

    if openupgrade.column_exists(cr, 'account_journal', 'allow_check_writing'):
        env.cr.execute(
            """\
            UPDATE account_payment ap
            SET
                payment_method_id = %s
            FROM account_voucher av
            INNER JOIN account_journal aj
            ON aj.id = av.journal_id
            WHERE ap.id = av.id
            AND aj.allow_check_writing = True
            AND ap.payment_type = 'outbound'
            """,
            (check_method.id,)
        )


@openupgrade.migrate(use_env=True)
def migrate(env, version):
    """Control function for account_voucher migration."""
    update_payments_from_vouchers(env)
