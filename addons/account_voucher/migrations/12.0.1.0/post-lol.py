# Copyright 2019 Eficent <http://www.eficent.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade


def fill_account_voucher_payment_journal_id(cr):
    openupgrade.logged_query(
        cr, """
        UPDATE account_voucher av
        SET payment_journal_id = ap.journal_id
        FROM account_payment ap
        INNER JOIN account_journal aj ON aj.id = ap.journal_id
        WHERE av.state != 'draft' AND av.pay_now = 'pay_now'
            AND ap.communication = av.name AND av.amount > 0
            AND ap.amount = av.amount AND ap.payment_date = av.date
            AND ap.currency_id = av.currency_id
            AND aj.type IN ('cash', 'bank')
            AND av.payment_journal_id IS NULL
        """
    )


@openupgrade.migrate()
def migrate(env, version):
    fill_account_voucher_payment_journal_id(env.cr)
