# SPDX-FileCopyrightText: 2024 Coop IT Easy SC
# SPDX-FileCopyrightText: 2024 Tecnativa - Pedro M. Baeza
# SPDX-License-Identifier: AGPL-3.0-or-later

from openupgradelib import openupgrade


def copy_session_id_to_line(cr):
    """There is no longer a link between account.bank.statement and pos.session.
    Instead, the link is between account.bank.statement.line and pos.session.
    """
    openupgrade.logged_query(
        cr,
        """
        UPDATE account_bank_statement_line line
        SET pos_session_id=statement.pos_session_id
        FROM account_bank_statement statement
        WHERE line.statement_id=statement.id
        """,
    )


def copy_register_balance(cr):
    """There is no longer a link between account.bank.statement and pos.session.
    The updated fields used to be related fields. Now, we store their values.
    """
    openupgrade.logged_query(
        cr,
        """
        UPDATE pos_session session
        SET cash_register_balance_end_real=statement.balance_end_real,
            cash_register_balance_start=statement.balance_start
        FROM account_bank_statement statement
        WHERE statement.pos_session_id=session.id
        """,
    )


@openupgrade.migrate()
def migrate(env, version):
    copy_session_id_to_line(env.cr)
    copy_register_balance(env.cr)
    openupgrade.delete_records_safely_by_xml_id(
        env,
        [
            "point_of_sale.rule_pos_cashbox_line_accountant",
            "point_of_sale.500_00",
        ],
    )
    openupgrade.load_data(env.cr, "point_of_sale", "16.0.1.0.1/noupdate_changes.xml")
