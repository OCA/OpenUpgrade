# Copyright 2020 ForgeFlow <http://www.forgeflow.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade


def set_account_move_number_to_invoice_number(env):
    """l10n_es_account_invoice_sequence introduced different numbering between
    invoices and account moves.

    As long as we have only account_moves in version 13 we have to choose one.
    In case that module is installed we trust the sequence of the invoice, but
    we move previously the move number to the reference for not losing it.

    It also assigns invoice sequences to the journals.
    """
    openupgrade.logged_query(
        env.cr, """
        UPDATE account_move am
        SET ref = regexp_replace(
            ref,
            CONCAT('( |^)', ai.invoice_number, '( |$)'),
            CONCAT('\1', am.name, '\2')
        )
        FROM account_invoice ai
        WHERE ai.move_id = am.id AND ai.invoice_number IS NOT NULL"""
    )
    openupgrade.logged_query(
        env.cr, """
        UPDATE account_move am SET name = ai.invoice_number
        FROM account_invoice ai
        WHERE ai.move_id = am.id AND ai.invoice_number IS NOT NULL"""
    )
    openupgrade.logged_query(
        env.cr, """
        UPDATE account_journal
        SET sequence_id = invoice_sequence_id
        WHERE invoice_sequence_id IS NOT NULL"""
    )
    openupgrade.logged_query(
        env.cr, """
        UPDATE account_journal
        SET refund_sequence_id = refund_inv_sequence_id,
            refund_sequence = True
        WHERE refund_inv_sequence_id IS NOT NULL"""
    )


@openupgrade.migrate()
def migrate(env, version):
    if openupgrade.column_exists(
            env.cr, "account_invoice", "invoice_number"):
        set_account_move_number_to_invoice_number(env)
