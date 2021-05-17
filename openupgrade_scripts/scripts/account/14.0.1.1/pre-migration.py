# Copyright 2021 ForgeFlow S.L.  <https://www.forgeflow.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade


def rename_fields(env):
    openupgrade.rename_fields(
        env,
        [
            (
                "account.bank.statement.line",
                "account_bank_statement_line",
                "name",
                "payment_ref",
            ),
            (
                "account.cash.rounding",
                "account_cash_rounding",
                "account_id",
                "profit_account_id",
            ),
            (
                "account.group",
                "account_group",
                "code_prefix",
                "code_prefix_start",
            ),
            (
                "account.move",
                "account_move",
                "invoice_partner_bank_id",
                "partner_bank_id",
            ),
            (
                "account.move",
                "account_move",
                "invoice_payment_ref",
                "payment_reference",
            ),
            (
                "account.move",
                "account_move",
                "invoice_sent",
                "is_move_sent",
            ),
            (
                "account.move",
                "account_move",
                "type",
                "move_type",
            ),
            (
                "account.move",
                "account_move",
                "invoice_payment_state",
                "payment_state",
            ),
            (
                "account.move.line",
                "account_move_line",
                "tag_ids",
                "tax_tag_ids",
            ),
            (
                "res.company",
                "res_company",
                "account_onboarding_sample_invoice_state",
                "account_onboarding_create_invoice_state",
            ),
            (
                "res.company",
                "res_company",
                "accrual_default_journal_id",
                "automatic_entry_default_journal_id",
            ),
        ],
    )


def copy_currency_id_and_journal_currency_id_fields(env):
    openupgrade.rename_columns(
        env.cr,
        {
            "account_bank_statement_line": [
                ("currency_id", None),
                ("journal_currency_id", None),
                ("id", None),
            ]
        },
    )


def m2m_tables_account_journal_renamed(env):
    openupgrade.rename_tables(
        env.cr,
        [
            ("account_account_type_rel", "journal_account_control_rel"),
            ("account_journal_type_rel", "journal_account_type_control_rel"),
        ],
    )


def copy_default_accounts_fields(env):
    openupgrade.rename_columns(
        env.cr,
        {
            "account.journal": [
                ("default_credit_account_id", None),
                ("default_debit_account_id", None),
            ]
        },
    )


def add_move_id_field_account_bank_statement_line(env):
    openupgrade.logged_query(
        env.cr,
        """
        ALTER TABLE account_bank_statement_line
        ADD move_id int
        """,
    )
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE account_bank_statement_line
        SET move_id = am.id
        FROM account_move am
        WHERE move_name = am.name
        """,
    )


def add_move_id_field_account_payment(env):
    openupgrade.logged_query(
        env.cr,
        """
        ALTER TABLE account_payment
        ADD move_id int
        """,
    )
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE account_payment
        SET move_id = am.id
        FROM account_move am
        WHERE move_name = am.name OR (
            payment_reference = am.name AND move_name IS NULL)
        """,
    )
    openupgrade.logged_query(
        env.cr,
        """
        ALTER TABLE account_move
        ADD payment_id int
        """,
    )
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE account_move
        SET payment_id = ap.id
        FROM account_payment ap
        WHERE account_move.id = ap.move_id
        """,
    )


def fill_empty_partner_type_account_payment(env):
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE account_payment
        SET partner_type = 'customer'
        WHERE partner_type IS NULL
        """,
    )


def renamed_noupdate_xmlids(env):
    openupgrade.rename_xmlids(
        env.cr,
        [
            (
                "account_analytic_default.analytic_default_comp_rule",
                "account.analytic_default_comp_rule",
            )
        ],
    )


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.set_xml_ids_noupdate_value(
        env, "account", ["account_analytic_line_rule_billing_user"], True
    )
    renamed_noupdate_xmlids(env)
    rename_fields(env)
    copy_currency_id_and_journal_currency_id_fields(env)
    m2m_tables_account_journal_renamed(env)
    copy_default_accounts_fields(env)
    add_move_id_field_account_bank_statement_line(env)
    add_move_id_field_account_payment(env)
    fill_empty_partner_type_account_payment(env)
