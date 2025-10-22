# Copyright 2025 Tecnativa - Carlos Lopez
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from openupgradelib import openupgrade


def fill_account_journal_debit_sequence(env):
    """
    Ensure that the debit_sequence column exists in the account_journal table.
    This column was previously part of the account_debit_note_sequence module,
    which has now been merged into account_debit_note.
    If the column does not exist,
    create it and set its default value to False to maintain the previous behavior.
    """
    if not openupgrade.column_exists(env.cr, "account_journal", "debit_sequence"):
        openupgrade.add_columns(
            env, [("account_journal", "debit_sequence", "boolean", False)]
        )


@openupgrade.migrate()
def migrate(env, version):
    fill_account_journal_debit_sequence(env)
