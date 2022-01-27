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
                "account.bank.statement.line",
                "account_bank_statement_line",
                "currency_id",
                "foreign_currency_id",
            ),
            (
                "account.bank.statement.line",
                "account_bank_statement_line",
                "journal_currency_id",
                "currency_id",
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


def m2m_tables_account_journal_renamed(env):
    openupgrade.rename_tables(
        env.cr,
        [
            ("account_account_type_rel", "journal_account_control_rel"),
            ("account_journal_type_rel", "journal_account_type_control_rel"),
        ],
    )


def remove_constrains_reconcile_models(env):
    openupgrade.remove_tables_fks(
        env.cr,
        [
            "account_reconcile_model_analytic_tag_rel",
            "account_reconcile_model_account_tax_rel",
            "account_reconcile_model_template_account_tax_template_rel",
            "account_reconcile_model_tmpl_account_tax_bis_rel",
        ],
    )
    openupgrade.logged_query(
        env.cr,
        """
        ALTER TABLE account_reconcile_model_analytic_tag_rel
        ALTER COLUMN account_reconcile_model_id DROP NOT NULL
        """,
    )
    openupgrade.logged_query(
        env.cr,
        """
        ALTER TABLE account_reconcile_model_analytic_tag_rel
        ADD COLUMN account_reconcile_model_line_id integer
        """,
    )


def copy_fields(env):
    openupgrade.rename_columns(
        env.cr,
        {
            "account_journal": [
                ("default_credit_account_id", None),
                ("default_debit_account_id", None),
            ],
        },
    )
    if openupgrade.column_exists(env.cr, "account_move", "move_type"):
        # see account_tax_balance of OCA
        openupgrade.rename_fields(
            env,
            [
                (
                    "account.move",
                    "account_move",
                    "move_type",
                    openupgrade.get_legacy_name("move_type"),
                ),
            ],
        )
    openupgrade.copy_columns(
        env.cr,
        {
            "account_bank_statement_line": [
                ("date", None, None),
            ],
            "account_payment": [
                ("journal_id", None, None),
                ("name", None, None),
                ("payment_date", None, None),
            ],
        },
    )


def add_move_id_field_account_bank_statement_line(env):
    if not openupgrade.column_exists(
        env.cr, "account_bank_statement_line", "currency_id"
    ):
        openupgrade.logged_query(
            env.cr,
            """
            ALTER TABLE account_bank_statement_line
            ADD COLUMN currency_id integer
            """,
        )
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE account_bank_statement_line absl
        SET currency_id = COALESCE(aj.currency_id, rc.currency_id)
        FROM account_bank_statement bs
        JOIN account_journal aj ON bs.journal_id = aj.id
        JOIN res_company rc ON aj.company_id = rc.id
        WHERE absl.statement_id = bs.id
        """,
    )
    if not openupgrade.column_exists(env.cr, "account_bank_statement_line", "move_id"):
        openupgrade.logged_query(
            env.cr,
            """
            ALTER TABLE account_bank_statement_line
            ADD COLUMN move_id integer
            """,
        )
    if not openupgrade.column_exists(env.cr, "account_move", "statement_line_id"):
        # In v10 existed that field
        openupgrade.logged_query(
            env.cr,
            """
            ALTER TABLE account_move
            ADD COLUMN statement_line_id integer
            """,
        )
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE account_move am
        SET statement_line_id = aml.statement_line_id
        FROM account_move_line aml
        WHERE aml.move_id = am.id AND aml.statement_line_id IS NOT NULL
        """,
    )
    # 1. set move_id from moves where statement_line_id is defined
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE account_bank_statement_line absl
        SET move_id = am.id
        FROM account_move am
        WHERE am.statement_line_id = absl.id
        """,
    )
    # 2. try to match on statement move_name or payment_ref (if move_name empty)
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE account_bank_statement_line absl
        SET move_id = am.id
        FROM account_move am, account_bank_statement bs
        WHERE absl.statement_id = bs.id
            AND absl.move_id IS NULL
            AND am.name NOT IN ('', '/')
            AND COALESCE(NULLIF(absl.move_name, ''), absl.payment_ref) = am.name
            AND am.company_id = bs.company_id
        """,
    )
    # 3. match on statement payment_ref with payment communication
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE account_bank_statement_line absl
        SET move_id = ap.move_id
        FROM account_payment ap
        JOIN account_journal aj ON ap.journal_id = aj.id,
            account_bank_statement bs
        WHERE absl.statement_id = bs.id AND aj.company_id = bs.company_id
            AND absl.move_id IS NULL AND absl.payment_ref NOT IN ('', '/')
            AND absl.payment_ref = ap.communication
        """,
    )
    # 4. match on statement account number and move ref
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE account_bank_statement_line absl
        SET move_id = am.id
        FROM account_move am, account_bank_statement bs
        WHERE absl.statement_id = bs.id AND am.company_id = bs.company_id
            AND absl.move_id IS NULL AND absl.account_number NOT IN ('', '/')
            AND absl.account_number = am.ref
        """,
    )
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE account_move am
        SET statement_line_id = absl.id
        FROM account_bank_statement_line absl
        WHERE am.id = absl.move_id AND am.statement_line_id IS NULL
        """,
    )


def add_move_id_field_account_payment(env):
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE account_payment ap
        SET currency_id = COALESCE(aj.currency_id, rc.currency_id)
        FROM account_journal aj
        JOIN res_company rc ON aj.company_id = rc.id
        WHERE ap.journal_id = aj.id
        """,
    )
    if not openupgrade.column_exists(env.cr, "account_payment", "move_id"):
        openupgrade.logged_query(
            env.cr,
            """
            ALTER TABLE account_payment
            ADD COLUMN move_id integer
            """,
        )
    if not openupgrade.column_exists(env.cr, "account_move", "payment_id"):
        openupgrade.logged_query(
            env.cr,
            """
            ALTER TABLE account_move
            ADD COLUMN payment_id integer
            """,
        )
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE account_move am
        SET payment_id = aml.payment_id
        FROM account_move_line aml
        WHERE aml.move_id = am.id AND aml.payment_id IS NOT NULL
        """,
    )
    # 1. set move_id from moves where payment_id is defined
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE account_payment ap
        SET move_id = am.id
        FROM account_move am
        WHERE am.payment_id = ap.id""",
    )
    # 2. try to match on payment move_name or payment_reference (if move_name empty)
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE account_payment ap
        SET move_id = am.id
        FROM account_move am, account_journal aj
        WHERE ap.journal_id = aj.id
            AND ap.move_id IS NULL
            AND am.name NOT IN ('', '/')
            AND COALESCE(NULLIF(ap.move_name, ''), ap.payment_reference) = am.name
            AND am.company_id = aj.company_id""",
    )
    # 3. match on payment communication with move payment_reference, ref or name
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE account_payment ap
        SET move_id = am.id
        FROM account_move am, account_journal aj
        WHERE ap.journal_id = aj.id AND am.company_id = aj.company_id AND
            ap.move_id IS NULL AND ap.communication NOT IN ('', '/') AND (
            am.payment_reference = ap.communication OR am.ref = ap.communication
            OR am.name = ap.communication)
        """,
    )
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE account_move am
        SET payment_id = ap.id
        FROM account_payment ap
        WHERE am.id = ap.move_id
        """,
    )


def add_edi_state_field_account_move(env):
    """
    Module account_edi: Created edi_state column and set the default value is false
    """
    if not openupgrade.column_exists(env.cr, "account_move", "edi_state"):
        openupgrade.logged_query(
            env.cr,
            """
            ALTER TABLE account_move
            ADD COLUMN edi_state varchar
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


def fill_account_move_line_currency_id(env):
    openupgrade.logged_query(
        env.cr,
        """
        ALTER TABLE account_move_line
        DROP CONSTRAINT IF EXISTS account_move_line_check_amount_currency_balance_sign
        """,
    )
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE account_move_line
        SET currency_id = company_currency_id
        WHERE currency_id IS NULL
        """,
    )


def fill_account_payment_partner_id(env):
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE account_payment ap
        SET partner_id = rc.partner_id
        FROM account_journal aj
        JOIN res_company rc ON aj.company_id = rc.id
        WHERE ap.payment_type = 'transfer'
        """,
    )


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.set_xml_ids_noupdate_value(
        env, "account", ["account_analytic_line_rule_billing_user"], True
    )
    copy_fields(env)
    rename_fields(env)
    m2m_tables_account_journal_renamed(env)
    remove_constrains_reconcile_models(env)
    add_move_id_field_account_payment(env)
    add_move_id_field_account_bank_statement_line(env)
    add_edi_state_field_account_move(env)
    fill_empty_partner_type_account_payment(env)
    fill_account_move_line_currency_id(env)
    fill_account_payment_partner_id(env)
    # Disappeared constraint
    openupgrade.logged_query(
        env.cr,
        """ALTER TABLE account_move_line
           DROP CONSTRAINT IF EXISTS
           account_move_line_check_amount_currency_balance_sign""",
    )
    openupgrade.delete_records_safely_by_xml_id(
        env, ["account.constraint_account_move_line_check_amount_currency_balance_sign"]
    )
