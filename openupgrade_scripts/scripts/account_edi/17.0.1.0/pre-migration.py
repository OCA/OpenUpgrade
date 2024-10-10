# Copyright 2023 Viindoo - Nguyễn Đại Dương
# Copyright 2024 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade


def _remove_table_constraints(env):
    openupgrade.delete_sql_constraint_safely(
        env,
        "account_edi",
        "account_edi_document",
        "account_edi_document_unique_edi_document_by_move_by_format",
    )
    openupgrade.delete_sql_constraint_safely(
        env, "account_edi", "account_edi_format", "account_edi_format_unique_code"
    )


@openupgrade.migrate()
def migrate(env, version):
    _remove_table_constraints(env)
