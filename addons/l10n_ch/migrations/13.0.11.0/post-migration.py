# Copyright 2021 ForgeFlow <http://www.forgeflow.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade


def move_from_invoices_to_moves(env):
    openupgrade.logged_query(
        env.cr, """
        UPDATE account_move am
        SET l10n_ch_isr_number = ai.l10n_ch_isr_number,
            l10n_ch_isr_sent = ai.l10n_ch_isr_sent
        FROM account_invoice ai
        WHERE am.old_invoice_id = ai.id""",
    )


def move_from_bank_to_partner_bank(env):
    openupgrade.logged_query(
        env.cr, """
        UPDATE res_partner_bank rpb
        SET l10n_ch_isr_subscription_chf = rb.l10n_ch_postal_chf,
            l10n_ch_isr_subscription_eur = rb.l10n_ch_postal_eur
        FROM res_bank rb
        WHERE rpb.bank_id = rb.id""",
    )


@openupgrade.migrate()
def migrate(env, version):
    move_from_invoices_to_moves(env)
    move_from_bank_to_partner_bank(env)
    openupgrade.load_data(
        env.cr, "l10n_ch", "migrations/13.0.11.0/noupdate_changes.xml")
