# Copyright 2020 ForgeFlow <http://www.forgeflow.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade


def set_account_move_number_to_invoice_number(env):
    """l10n_es_account_invoice_sequence introduced different numbering between
    invoices and account moves.
    As long as we have only account_moves in version 13 we have to choose one.
    In case that module is installed we trust the sequence of the invoice
    """
    openupgrade.logged_query(
        env.cr, """
        UPDATE account_move am0 SET name = ai.invoice_number
        FROM account_invoice ai INNER JOIN account_move am
        ON ai.move_id = am.id
        WHERE ai.invoice_number is not null
        AND am.id = am0.id
        """
    )


@openupgrade.migrate()
def migrate(env, version):
    if openupgrade.column_exists(
            env.cr, "account_invoice", "invoice_number"):
        set_account_move_number_to_invoice_number(env)
