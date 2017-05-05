# -*- coding: utf-8 -*-
# © 2016 Therp BV <http://therp.nl>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade


def create_payments_from_vouchers(env):
    """Create account.payment rows from appropiate account.voucher rows."""
    receipt_method = env.ref('account.account_payment_method_manual_in')
    payment_method = env.ref('account.account_payment_method_manual_out')
    # Keep original id, to later migrate references from other tables,
    # although it seems not te be needed for now.
    # Possible states of account.payment: draft, posted, sent, reconciled
    # Possible states of account_voucher: draft, cancel, proforma, posted
    # "type" field in 8.0 renamed to "voucher_type" during migration.
    # Field destination_journal_id is used for internal transfer payments.
    # Not used here.
    # As far as I can see there is no connection between invoices in 8.0
    # that we can or have to migrate to 9.0.
    env.cr.execute(
        """\
        INSERT INTO account_payment (
            id, create_date, communication, company_id, currency_id,
            partner_id, partner_type,
            payment_method_id, payment_date, payment_difference_handling,
            journal_id,
            state, writeoff_account_id, create_uid, write_date, write_uid,
            name, amount, payment_type, payment_reference
        )
        SELECT
            av.id, av.create_date, av.comment, av.company_id,
            av.payment_rate_currency_id, av.partner_id,
            CASE
               WHEN av.voucher_type = 'receipt' THEN 'customer'
               ELSE 'supplier'
            END,
            CASE WHEN av.voucher_type = 'receipt' THEN %s ELSE %s END,
            av.create_date,
            CASE
                WHEN av.payment_option = 'with_writeoff' THEN 'reconcile'
                ELSE 'open'
            END,
            av.journal_id, av.state, av.writeoff_acc_id, av.create_uid,
            av.write_date, av.write_uid,
            COALESCE(av.name, av.comment),
            av.amount,
            CASE
               WHEN av.voucher_type = 'receipt' THEN 'inbound'
               ELSE 'outbound'
            END,
            av.reference
        FROM account_voucher av
        WHERE av.voucher_type IN ('receipt', 'payment')
        AND av.state in ('draft', 'posted')
        """,
        (receipt_method.id,
         payment_method.id)
    )
    env.cr.execute(
        """SELECT COALESCE(MAX(id), 0) AS max_id FROM account_payment"""
    )
    max_id = env.cr.fetchone()[0] + 1
    env.cr.execute(
        """ALTER SEQUENCE account_payment_id_seq RESTART WITH %s""",
        (max_id,)
    )
    # Statement below works because new payments have same id as old vouchers
    env.cr.execute(
        """\
        UPDATE account_move_line aml2
        SET payment_id = av.id
        FROM account_voucher av
        JOIN account_move am
        ON am.id = av.move_id
        JOIN account_move_line aml
        ON am.id = aml.move_id
        WHERE av.voucher_type IN ('receipt', 'payment')
        AND (av.writeoff_acc_id != aml.account_id
             OR av.writeoff_acc_id IS NULL)
        AND av.state in ('draft', 'posted')
        AND aml.id = aml2.id
        """
    )
    # Also recreate link from invoice to payment
    env.cr.execute(
        """\
        INSERT INTO account_invoice_payment_rel (payment_id, invoice_id)
        SELECT aml.payment_id, ai.id
        FROM account_move_line aml
        JOIN account_invoice ai ON aml.move_id = ai.move_id
        WHERE NOT aml.payment_id IS NULL
        GROUP BY aml.payment_id, ai.id
        """
    )


def create_voucher_line_tax_lines(env):
    """Migrate tax information on voucher lines to m2m relation."""
    env.cr.execute(
        "insert into account_tax_account_voucher_line_rel "
        "(account_tax_id, account_voucher_line_id) "
        "select v.tax_id, l.id "
        "from account_voucher v "
        "join account_voucher_line l on l.voucher_id=v.id "
        "where v.tax_id is not null")


@openupgrade.migrate(use_env=True)
def migrate(env, version):
    """Control function for account_voucher migration."""
    create_payments_from_vouchers(env)
    create_voucher_line_tax_lines(env)
