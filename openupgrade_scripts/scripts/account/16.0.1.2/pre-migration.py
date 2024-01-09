# Copyright 2023 Viindoo - Trịnh Ngọc Hưng
# Copyright 2023 Viindoo - Nguyễn Đại Dương
# Copyright 2023 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade, openupgrade_160

_xmlids_renames = [
    (
        "sale.group_delivery_invoice_address",
        "account.group_delivery_invoice_address",
    ),
]
_column_renames = {
    "account_move": [
        ("auto_post", None),
    ],
}
_fields_renames = [
    (
        "account.analytic.line",
        "account_analytic_line",
        "move_id",
        "move_line_id",
    ),
    (
        "account.tax.repartition.line.template",
        "account_tax_repartition_line_template",
        "minus_report_line_ids",
        "minus_report_expression_ids",
    ),
    (
        "account.tax.repartition.line.template",
        "account_tax_repartition_line_template",
        "plus_report_line_ids",
        "plus_report_expression_ids",
    ),
]
_models_renames = [
    ("account.tax.report", "account.report"),
    ("account.tax.carryover.line", "account.report.external.value"),
    ("account.tax.report.line", "account.report.line"),
]
_tables_renames = [
    ("account_tax_report", "account_report"),
    ("account_tax_carryover_line", "account_report_external_value"),
    ("account_tax_report_line", "account_report_line"),
]


def _fill_account_account_type(env, table):
    """Fill the account type deducing it from old types.
    Used for both account.account and account.account.template.
    """
    openupgrade.logged_query(
        env.cr,
        f"""
        ALTER TABLE {table}
        ADD COLUMN IF NOT EXISTS account_type VARCHAR
        """,
    )
    openupgrade.logged_query(
        env.cr,
        f"""
        WITH account_type_map AS (
            SELECT
                res_id AS user_type_id,
                CASE
                    WHEN name = 'data_account_type_receivable' THEN 'asset_receivable'
                    WHEN name = 'data_account_type_payable' THEN 'liability_payable'
                    WHEN name = 'data_account_type_liquidity' THEN 'asset_cash'
                    WHEN name = 'data_account_type_credit_card' THEN 'liability_credit_card'
                    WHEN name = 'data_account_type_current_assets' THEN 'asset_current'
                    WHEN name = 'data_account_type_non_current_assets' THEN 'asset_non_current'
                    WHEN name = 'data_account_type_prepayments' THEN 'asset_prepayments'
                    WHEN name = 'data_account_type_fixed_assets' THEN 'asset_fixed'
                    WHEN name = 'data_account_type_current_liabilities'
                        THEN 'liability_current'
                    WHEN name = 'data_account_type_non_current_liabilities'
                        THEN 'liability_non_current'
                    WHEN name = 'data_account_type_equity' THEN 'equity'
                    WHEN name = 'data_unaffected_earnings' THEN 'equity_unaffected'
                    WHEN name = 'data_account_type_revenue' THEN 'income'
                    WHEN name = 'data_account_type_other_income' THEN 'income_other'
                    WHEN name = 'data_account_type_expenses' THEN 'expense'
                    WHEN name = 'data_account_type_depreciation' THEN 'expense_depreciation'
                    WHEN name = 'data_account_type_direct_costs' THEN 'expense_direct_cost'
                    ELSE 'off_balance'
                END AS account_type
            FROM ir_model_data
            WHERE module='account' AND model = 'account.account.type'
        )
        UPDATE {table} aa
            SET account_type = atm.account_type
        FROM account_type_map atm
        WHERE atm.user_type_id = aa.user_type_id
        """,
    )
    # Fill the rest of "custom types" with `off_balance` type
    openupgrade.logged_query(
        env.cr,
        f"""
        UPDATE {table}
        SET account_type='off_balance'
        WHERE account_type IS NULL
        """,
    )


def _fill_account_account_include_initial_balance(env):
    """Fill include_initial_balance from the old account type."""
    openupgrade.logged_query(
        env.cr,
        """
        ALTER TABLE account_account
        ADD COLUMN IF NOT EXISTS include_initial_balance BOOL
        """,
    )
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE account_account aa
        SET include_initial_balance = aat.include_initial_balance
        FROM account_account_type aat
        WHERE aat.id = aa.user_type_id
        """,
    )


def _delete_sql_constraints(env):
    # Delete constraints to recreate it
    openupgrade.delete_sql_constraint_safely(
        env, "account", "account_journal", "code_company_uniq"
    )
    openupgrade.delete_sql_constraint_safely(
        env, "account", "account_move_line", "check_accountable_required_fields"
    )
    openupgrade.delete_sql_constraint_safely(
        env, "account", "account_move_line", "check_amount_currency_balance_sign"
    )
    openupgrade.delete_sql_constraint_safely(
        env, "account", "account_move_line", "check_credit_debit"
    )


def _account_bank_statement_line_fast_fill_internal_index(env):
    if not openupgrade.column_exists(
        env.cr, "account_bank_statement_line", "internal_index"
    ):
        openupgrade.add_fields(
            env,
            [
                (
                    "internal_index",
                    "account.bank.statement.line",
                    "account_bank_statement_line",
                    "char",
                    False,
                    "account",
                )
            ],
        )
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE account_bank_statement_line stmt
        SET internal_index = concat(
            to_char(am.date, 'YYYYMMDD'),
            lpad((2147483647 - stmt.sequence)::text, 10, '0'),
            lpad(am.id::text, 10, '0')
        )
        FROM account_move am
        WHERE stmt.move_id = am.id;
        """,
    )


def _account_move_fast_fill_display_type(env):
    """
    Respectively Fill display type is Null AND
    Case 1: with am is not invoice
            set display type is 'product'
    Case 2: with am is invoice AND aml line tax
            set display type is 'tax'
    Case 3: with am is invoice AND aml line receivable or payable,
            set display type is 'payment_term'
    Case 4: with am is invoice
            set display type is 'product'
    Case 5: with aml is an accounting transaction occurring
            set display type is 'product'
    """
    openupgrade.logged_query(
        env.cr,
        """
        WITH sub AS (
            SELECT
                aml.id,
                CASE
                    WHEN am.move_type NOT IN
                    ('out_invoice', 'out_refund', 'in_invoice', 'in_refund')
                    THEN 'product'
                    WHEN aml.tax_line_id IS NOT NULL THEN 'tax'
                    WHEN aa.account_type IN
                    ('asset_receivable', 'liability_payable') THEN 'payment_term'
                    ELSE 'product'
                END AS display_type
            FROM account_move_line AS aml
            LEFT JOIN account_move AS am ON am.id = aml.move_id
            LEFT JOIN account_account AS aa ON aa.id = aml.account_id
            WHERE aml.display_type IS NULL AND am.id = aml.move_id
        )
        UPDATE account_move_line AS aml
           SET display_type = sub.display_type
        FROM sub
        WHERE aml.id = sub.id;
        """,
    )


def _account_move_auto_post_boolean_to_selection(env):
    openupgrade.logged_query(
        env.cr,
        "ALTER TABLE account_move ADD COLUMN auto_post VARCHAR",
    )
    openupgrade.logged_query(
        env.cr,
        f"""
        UPDATE account_move AS am
        SET auto_post =
        CASE
            WHEN {openupgrade.get_legacy_name('auto_post')}
            THEN 'at_date'
            ELSE 'no'
        END;
        """,
    )


def _account_analytic_distribution_model_generate(env):
    openupgrade.logged_query(
        env.cr,
        "ALTER TABLE account_analytic_distribution_model "
        "ADD COLUMN IF NOT EXISTS partner_id INT4",
    )
    openupgrade.logged_query(
        env.cr,
        "ALTER TABLE account_analytic_distribution_model "
        "ADD COLUMN IF NOT EXISTS product_id INT4",
    )
    openupgrade.logged_query(
        env.cr,
        "ALTER TABLE account_analytic_distribution_model "
        "ADD COLUMN IF NOT EXISTS company_id INT4",
    )
    openupgrade.logged_query(
        env.cr,
        "ALTER TABLE account_analytic_distribution_model "
        "ADD COLUMN IF NOT EXISTS account_prefix VARCHAR",
    )
    openupgrade.logged_query(
        env.cr,
        """
        WITH distribution_data AS (
            WITH sub AS (
                SELECT
                    all_line_data.analytic_default_id,
                    all_line_data.analytic_account_id,
                    SUM(all_line_data.percentage) AS percentage
                FROM (
                    SELECT
                        analytic_default.id AS analytic_default_id,
                        account.id AS analytic_account_id,
                        100 AS percentage
                    FROM account_analytic_default analytic_default
                    JOIN account_analytic_account account
                        ON account.id = analytic_default.analytic_id
                    WHERE analytic_default.analytic_id IS NOT NULL
                    UNION ALL
                    SELECT
                        analytic_default.id AS analytic_default_id,
                        dist.account_id AS analytic_account_id,
                        dist.percentage AS percentage
                    FROM account_analytic_default analytic_default
                    JOIN account_analytic_default_account_analytic_tag_rel tag_rel
                        ON tag_rel.account_analytic_default_id = analytic_default.id
                    JOIN account_analytic_distribution dist
                        ON dist.tag_id = tag_rel.account_analytic_tag_id
                    JOIN account_analytic_tag aat
                            ON aat.id = tag_rel.account_analytic_tag_id
                    WHERE aat.active_analytic_distribution = true
                ) AS all_line_data
                GROUP BY all_line_data.analytic_default_id, all_line_data.analytic_account_id
            )
            SELECT sub.analytic_default_id AS analytic_default_id,
             jsonb_object_agg(sub.analytic_account_id::text, sub.percentage)
                 AS analytic_distribution
            FROM sub
            GROUP BY sub.analytic_default_id
        )
        INSERT INTO account_analytic_distribution_model (
            account_prefix,
            partner_id,
            product_id,
            company_id,
            create_date,
            write_date,
            create_uid,
            write_uid,
            analytic_distribution)
        SELECT
            aa.code,
            aad.partner_id,
            aad.product_id,
            COALESCE(aad.company_id, aaa.company_id, aa.company_id),
            aad.create_date,
            aad.write_date,
            aad.create_uid,
            aad.write_uid,
            dist.analytic_distribution
        FROM
            distribution_data dist
        JOIN account_analytic_default aad ON aad.id = dist.analytic_default_id
        LEFT JOIN account_analytic_account aaa ON aaa.id = aad.analytic_id
        LEFT JOIN account_account aa ON aa.id = aad.account_id
        """,
    )


def _fast_fill_account_payment_amount_company_currency_signed(env):
    """Avoid the heavy recomputation of this field precreating the column and
    filling it for the simple case. The rest will be done on post-migration.
    """
    openupgrade.logged_query(
        env.cr,
        "ALTER TABLE account_payment "
        "ADD COLUMN IF NOT EXISTS amount_company_currency_signed numeric",
    )
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE account_payment ap
        SET amount_company_currency_signed = (
            CASE
                WHEN payment_type = 'inbound'
                THEN amount
                ELSE -amount
            END
        )
        FROM res_company rc,
            account_move am
        WHERE ap.currency_id = rc.currency_id
            AND am.id = ap.move_id
            AND rc.id = am.company_id
        """,
    )


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.rename_xmlids(env.cr, _xmlids_renames)
    openupgrade.rename_columns(env.cr, _column_renames)
    openupgrade.rename_fields(env, _fields_renames)
    openupgrade.rename_models(env.cr, _models_renames)
    openupgrade.rename_tables(env.cr, _tables_renames)
    _fill_account_account_type(env, "account_account")
    _fill_account_account_type(env, "account_account_template")
    _fill_account_account_include_initial_balance(env)
    _delete_sql_constraints(env)
    _account_bank_statement_line_fast_fill_internal_index(env)
    _account_move_fast_fill_display_type(env)
    _account_move_auto_post_boolean_to_selection(env)
    _account_analytic_distribution_model_generate(env)
    openupgrade_160.fill_analytic_distribution(
        env,
        "account_move_line",
        "account_analytic_tag_account_move_line_rel",
        "account_move_line_id",
    )
    openupgrade_160.fill_analytic_distribution(
        env,
        "account_reconcile_model_line",
        "account_reconcile_model_analytic_tag_rel",
        "account_reconcile_model_line_id",
    )
    _fast_fill_account_payment_amount_company_currency_signed(env)
