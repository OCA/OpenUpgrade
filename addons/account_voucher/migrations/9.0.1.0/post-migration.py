# -*- coding: utf-8 -*-
# © 2016 Therp BV <http://therp.nl>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade


def get_ref(cr, module, xml_id):
    """Get reference (res_id) from module and xml_id from ir_model_data."""
    cr.execute("""
        SELECT res_id
        FROM ir_model_data
        WHERE module = %s AND name = %s
    """, (module, xml_id))
    return cr.fetchone()[0]


def migrate_voucher_types(cr):
    """Migrate voucher types."""
    # TODO: Should we really keep receipt and payment records? Might contain
    # duplicate info with the sales and purchases for which they have been
    # made, especially now that we migrate to account.payment.
    openupgrade.map_values(
        cr, openupgrade.get_legacy_name('type'), 'voucher_type',
        [('receipt', 'sale'), ('payment', 'purchase')],
        table='account_voucher')

def create_voucher_line_tax_lines(cr):
    """Migrate tax information on voucher lines to m2m relation."""
    cr.execute(
        "insert into account_tax_account_voucher_line_rel "
        "(account_tax_id, account_voucher_line_id) "
        "select v.tax_id, l.id "
        "from account_voucher v "
        "join account_voucher_line l on l.voucher_id=v.id "
        "where v.tax_id is not null")

def create_payments_from_vouchers(cr):
    """Create account.payment rows from appropiate account.voucher rows."""
    receipt_method = get_ref(
        cr, 'account', 'account_payment_method_manual_in'
    )
    payment_method = get_ref(
        cr, 'account', 'account_payment_method_manual_out'
    )
    # Keep original id, to later migrate references from other tables,
    # although it seems not te be needed for now.
    # Possible states of account.payment: draft, posted, sent, reconciled
    # Possible states of account_voucher: draft, cancel, proforma, posted
    # "type" field in 8.0 renamed to "voucher_type" during migration.
    # Field destination_journal_id is used for internal transfer payments.
    # Not used here.
    # As far as I can see there is no connection between invoices or moves
    # in 8.0 taht we can or have to migrate to 9.0.
    cr.execute("""
        INSERT INTO account_payment (
            id, create_date, communication, company_id, currency_id,
            partner_id, partner_type,
            payment_method_id, payment_date, payment_difference_handling,
            journal_id,
            state, writeoff_account_id, create_uid, write_date, write_uid,
            name, amount, payment_type, payment_reference
        )
        SELECT
            v.id, v.create_date, v.comment, v.company_id,
            v.payment_rate_currency_id, v.partner_id,
            CASE
               WHEN v.voucher_type = 'receipt' THEN 'customer'
               ELSE 'supplier'
            END,
            CASE WHEN v.voucher_type = 'receipt' THEN %s ELSE %s END,
            v.create_date,
            CASE
                WHEN v.payment_option = 'with_writeoff' THEN 'reconcile'
                ELSE 'open'
            END,
            v.journal_id, v.state, v.writeoff_acc_id, v.create_uid,
            v.write_date, v.write_uid,
            COALESCE(v.name, v.comment),
            v.amount,
            CASE
               WHEN v.voucher_type = 'receipt' THEN 'inbound'
               ELSE 'outbound'
            END,
            v.reference
        FROM account_voucher v
        WHERE v.voucher_type IN ('receipt', 'payment')
        AND v.state in ('draft', 'posted')""",
        (receipt_method, payment_method)
    )
    cr.execute(
        """SELECT COALESCE(MAX(id), 0) AS max_id FROM account_payment"""
    )
    max_id = cr.fetchone()[0] + 1
    cr.execute(
        """ALTER SEQUENCE account_payment_id_seq RESTART WITH %s""",
        (max_id,)
    )


@openupgrade.migrate()
def migrate(cr, version):
    """Control function for account_voucher migration."""
    create_payments_from_vouchers(cr)
    migrate_voucher_types(cr)
    create_voucher_line_tax_lines(cr)
