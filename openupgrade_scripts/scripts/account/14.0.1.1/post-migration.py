# Copyright 2021 ForgeFlow S.L.  <https://www.forgeflow.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade


def fill_foreign_currency_id_and_currency_id_field(env):
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE account_bank_statement_line
        SET currency_id = {}, foreign_currency_id = {}
        WHERE id = {}
        """.format(
            openupgrade.get_legacy_name("journal_currency_id"),
            openupgrade.get_legacy_name("currency_id"),
            openupgrade.get_legacy_name("id"),
        ),
    )


def fill_code_prefix_end_field(env):
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE account_bank_statement_line
        SET code_prefix_end = code_prefix_start
        """,
    )


def fill_default_account_id_field(env):
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE account_journal
        SET default_account_id = {0}
        WHERE {0} = {1} OR ({0} IS NOT NULL AND {1} IS NULL)
        UPDATE account_journal
        SET default_account_id = {1}
        WHERE {0} IS NULL AND {1} IS NOT NULL
        """.format(
            openupgrade.get_legacy_name("default_credit_account_id"),
            openupgrade.get_legacy_name("default_debit_account_id"),
        ),
    )


def fill_payment_id_and_statement_line_id_fields(env):
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE account_move_line
        SET payment_id = am.payment_id
        FROM account_move am
        WHERE am.id = account_move_line.move_id
        """,
    )
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE account_move_line
        SET statement_line_id = am.statement_line_id
        FROM account_move am
        WHERE am.id = account_move_line.move_id
        """,
    )


def fill_active_field_account_reconcile_model(env):
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE account_reconcile_model
        SET active = TRUE
        """,
    )


def fill_matching_order_field_default(env):
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE account_reconcile_model_template
        SET matching_order = 'old_first'
        WHEN matching_order IS NULL
        """,
    )


def try_delete_noupdate_records(env):
    openupgrade.delete_records_safely_by_xml_id(
        env,
        [
            "account.sequence_payment_customer_invoice",
            "account.sequence_payment_customer_refund",
            "account.sequence_payment_supplier_invoice",
            "account.sequence_payment_supplier_refund",
            "account.sequence_payment_transfer",
        ],
    )


@openupgrade.migrate()
def migrate(env, version):
    fill_foreign_currency_id_and_currency_id_field(env)
    fill_code_prefix_end_field(env)
    fill_default_account_id_field(env)
    fill_payment_id_and_statement_line_id_fields(env)
    fill_active_field_account_reconcile_model(env)
    fill_matching_order_field_default(env)
    openupgrade.load_data(env.cr, "account", "14.0.1.0/noupdate_changes.xml")
    try_delete_noupdate_records(env)
