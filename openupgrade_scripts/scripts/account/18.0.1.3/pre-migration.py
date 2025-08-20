# Copyright 2025 ForgeFlow S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from openupgradelib import openupgrade

field_renames = [
    ("account.move", "account_move", "payment_id", "origin_payment_id"),
    ("account.move", "account_move", "reversal_move_id", "reversal_move_ids"),
    ("account.move", "account_move", "send_and_print_values", "sending_data"),
    (
        "account.payment",
        "account_payment",
        "journal_id",
        "old_journal_id",
    ),  # to avoid conflict in ir.model.fields
    ("account.payment", "account_payment", "destination_journal_id", "journal_id"),
]

field_renames_l10n_dk_bookkeeping = [
    (
        "account.move",
        "account_move",
        "l10n_dk_currency_rate_at_transaction",
        "invoice_currency_rate",
    ),
]

_new_columns = [
    ("account.bank.statement.line", "company_id", "many2one"),
    ("account.bank.statement.line", "journal_id", "many2one"),
    ("account.journal", "autocheck_on_post", "boolean", True),
    ("account.move", "amount_untaxed_in_currency_signed", "float"),
    ("account.move", "checked", "boolean"),
    ("account.move", "preferred_payment_method_line_id", "many2one"),
    ("account.reconcile.model", "counterpart_type", "selection", "general"),
    ("account.tax", "price_include_override", "selection", "tax_excluded"),
    ("account.payment", "name", "char"),
    ("account.payment", "date", "date"),
    ("account.payment", "memo", "char"),
    ("account.payment", "state", "selection"),
    ("account.payment", "is_sent", "boolean"),
]


def rename_selection_option(env):
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE account_account
        SET internal_group = 'off'
        WHERE internal_group = 'off_balance'""",
    )
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE account_report
        SET default_opening_date_filter = 'last_' || substr(
            default_opening_date_filter, 10)
        WHERE left(default_opening_date_filter, 9) = 'previous_'""",
    )
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE account_report_expression
        SET date_scope = 'strict_range'
        WHERE date_scope = 'normal'""",
    )
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE account_tax
        SET price_include_override = 'tax_included'
        WHERE price_include""",
    )


def update_account_move_amount_untaxed_in_currency_signed(env):
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE account_move
        SET amount_untaxed_in_currency_signed = CASE
            WHEN move_type IN ('out_invoice', 'in_refund', 'out_receipt')
                THEN COALESCE(amount_untaxed, 0.0)
            ELSE (-1) * COALESCE(amount_untaxed, 0.0) END""",
    )


def update_account_move_checked(env):
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE account_move
        SET checked = TRUE
        WHERE to_check IS DISTINCT FROM TRUE""",
    )


def fill_account_move_preferred_payment_method_line_id(env):
    if openupgrade.column_exists(env.cr, "account_move", "preferred_payment_method_id"):
        # having account_check_printing module
        openupgrade.logged_query(
            env.cr,
            """
            UPDATE account_move am2
            SET preferred_payment_method_line_id = COALESCE(apml.id, apml2.id)
            FROM account_move am
            JOIN account_payment_method apm ON
                apm.id = am.preferred_payment_method_id
            LEFT JOIN account_payment_method_line apml ON
                apml.payment_method_id = apm.id AND apml.journal_id = am.journal_id
            LEFT JOIN account_payment_method_line apml2 ON
                apml2.payment_method_id = apm.id AND apml2.journal_id IS NULL
            WHERE am.id = am2.id""",
        )


def adapt_account_move_sending_data(env):
    # sp_partner_id -> author_partner_id:
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE account_move
        SET sending_data = jsonb_set(sending_data::jsonb - 'sp_partner_id',
            '{author_partner_id}', sending_data::jsonb->'sp_partner_id')
        WHERE sending_data IS NOT NULL AND sending_data::jsonb ? 'sp_partner_id'""",
    )
    # sp_user_id -> author_user_id:
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE account_move
        SET sending_data = jsonb_set(sending_data::jsonb - 'sp_user_id',
            '{author_user_id}', sending_data::jsonb->'sp_user_id')
        WHERE sending_data IS NOT NULL AND sending_data::jsonb ? 'sp_user_id'""",
    )
    # send_mail: True -> 'sending_methods': ["email"]:
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE account_move
        SET sending_data = jsonb_set(sending_data::jsonb - 'send_mail',
            '{sending_methods}', '["email"]'::jsonb)
        WHERE sending_data IS NOT NULL
            AND sending_data::jsonb @> '{"send_mail": "true"}'::jsonb""",
    )


def fill_account_payment(env):
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE account_payment ap
        SET memo = am.ref,
            state= CASE WHEN am.state = 'cancel' THEN 'canceled'
                        WHEN am.payment_state = 'paid' THEN 'paid'
                        WHEN am.state = 'posted' THEN 'in_process'
                        ELSE am.state END,
            is_sent = am.is_move_sent,
            name = CASE WHEN am.name != '/' THEN am.name
                        ELSE 'Draft Payment' END,
            date = am.date,
            journal_id = CASE WHEN ap.journal_id IS NULL
                                AND aj.type in ('bank', 'cash', 'credit')
                              THEN am.journal_id ELSE ap.journal_id END
        FROM account_move am
        LEFT JOIN account_journal aj ON am.journal_id = aj.id
        WHERE ap.move_id = am.id""",
    )


def fill_statement_line_fields(env):
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE account_bank_statement_line sl
        SET company_id = mv.company_id
        FROM account_move mv
        WHERE sl.move_id = mv.id""",
    )
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE account_bank_statement_line sl
        SET journal_id = mv.journal_id
        FROM account_move mv
        WHERE sl.move_id = mv.id""",
    )


@openupgrade.migrate()
def migrate(env, version):
    if openupgrade.column_exists(env.cr, "account_cash_rounding", "profit_account_id"):
        # in v13, these fields were not company_dependent
        field_names = ["profit_account_id"]
        if openupgrade.column_exists(
            env.cr, "account_cash_rounding", "loss_account_id"
        ):
            # loss_account_id came from pos_cash_rounding
            field_names += ["loss_account_id"]
        openupgrade.rename_columns(
            env.cr,
            {
                "account_cash_rounding": [
                    (field_name, None) for field_name in field_names
                ]
            },
        )
    if openupgrade.column_exists(env.cr, "res_partner", "credit_limit"):
        # in v15, this field was not company_dependent
        openupgrade.rename_columns(
            env.cr,
            {"res_partner": [("credit_limit", None)]},
        )
    if openupgrade.column_exists(
        env.cr, "account_move", "l10n_dk_currency_rate_at_transaction"
    ):
        openupgrade.rename_fields(env, field_renames_l10n_dk_bookkeeping)
    openupgrade.rename_fields(env, field_renames)
    openupgrade.add_columns(env, _new_columns)
    update_account_move_amount_untaxed_in_currency_signed(env)
    update_account_move_checked(env)
    fill_account_move_preferred_payment_method_line_id(env)
    adapt_account_move_sending_data(env)
    rename_selection_option(env)
    fill_account_payment(env)
    fill_statement_line_fields(env)
    openupgrade.convert_field_to_html(
        env.cr,
        "account_tax",
        "description",
        "description",
        verbose=False,
        translate=True,
    )
    openupgrade.delete_records_safely_by_xml_id(
        env,
        [
            "account.action_account_unreconcile",
        ],
    )
