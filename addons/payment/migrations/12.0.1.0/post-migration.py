# Copyright 2018 Eficent <http://www.eficent.com>
# Copyright 2018 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade


def map_payment_transaction_state(cr):
    openupgrade.map_values(
        cr,
        openupgrade.get_legacy_name('state'),
        'state',
        [('refunding', 'cancel'),
         ('refunded', 'cancel'),
         ],
        table='payment_transaction', write='sql')


def fill_payment_transaction_is_processed(cr):
    openupgrade.logged_query(
        cr, """
        UPDATE payment_transaction
        SET is_processed = True""",
    )


def fill_payment_transaction_payment_id(cr):
    openupgrade.logged_query(
        cr, """
        UPDATE payment_transaction pt
        SET payment_id = COALESCE(pt.payment_id, ap.id)
        FROM account_payment ap
        WHERE ap.payment_transaction_id = pt.id""",
    )


def fill_invoice_ids(env):
    """Fill invoice_ids field in payment.transaction, and recompute nbr."""
    openupgrade.logged_query(
        env.cr, """
        INSERT INTO account_invoice_transaction_rel
        (transaction_id, invoice_id)
        SELECT pt.id, ai_rel.invoice_id
        FROM account_payment ap,
            payment_transaction pt,
            account_invoice_payment_rel ai_rel
        WHERE ap.payment_transaction_id = pt.id
            AND ai_rel.payment_id = ap.id
        """,
    )
    env['payment.transaction'].search([])._compute_invoice_ids_nbr()


def fill_missing_acquirers_journals(env):
    """There's a new check in sale.order._create_payment_transaction() method
    that avoids to create the payment transaction (although is not needed at
    all), so we prevent the problem creating/assigning the missing journals
    in payment acquirers through the helper that the core offers.
    """
    companies = env["res.company"].search([])
    Acquirer = env["payment.acquirer"]
    for company in companies:
        Acquirer._create_missing_journal_for_acquirers(company=company)


@openupgrade.migrate()
def migrate(env, version):
    cr = env.cr
    map_payment_transaction_state(cr)
    fill_payment_transaction_is_processed(cr)
    fill_payment_transaction_payment_id(cr)
    fill_invoice_ids(env)
    fill_missing_acquirers_journals(env)
    openupgrade.load_data(
        cr, 'payment', 'migrations/12.0.1.0/noupdate_changes.xml')
