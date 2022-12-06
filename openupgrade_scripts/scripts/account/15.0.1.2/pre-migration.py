from openupgradelib import openupgrade

from odoo.tools import sql

_renamed_fields = [
    (
        "account.move",
        "account_move",
        "tax_cash_basis_move_id",
        "tax_cash_basis_origin_move_id",
    ),
    (
        "account.reconcile.model",
        "account_reconcile_model",
        "match_total_amount_param",
        "payment_tolerance_param",
    ),
    (
        "account.reconcile.model.template",
        "account_reconcile_model_template",
        "match_total_amount_param",
        "payment_tolerance_param",
    ),
    (
        "account.reconcile.model",
        "account_reconcile_model",
        "match_total_amount",
        "allow_payment_tolerance",
    ),
    (
        "account.reconcile.model.template",
        "account_reconcile_model_template",
        "match_total_amount",
        "allow_payment_tolerance",
    ),
    (
        "res.company",
        "res_company",
        "account_tax_fiscal_country_id",
        "account_fiscal_country_id",
    ),
]


def switch_payment_tolerance_param_value(env):
    for table in ["account_reconcile_model", "account_reconcile_model_template"]:
        openupgrade.logged_query(
            env.cr,
            f"""
            UPDATE {table}
            SET payment_tolerance_param = 100.0 - COALESCE(payment_tolerance_param, 0.0)
            """,
        )


def _convert_field_to_html(env):
    openupgrade.convert_field_to_html(
        env.cr, "res_company", "invoice_terms", "invoice_terms"
    )
    openupgrade.convert_field_to_html(env.cr, "account_fiscal_position", "note", "note")
    openupgrade.convert_field_to_html(
        env.cr, "account_move", "narration", "narration", verbose=False
    )
    openupgrade.convert_field_to_html(env.cr, "account_payment_term", "note", "note")


def _fast_fill_account_move_always_tax_exigible(env):
    openupgrade.logged_query(
        env.cr,
        """
        ALTER TABLE account_move
        ADD COLUMN IF NOT EXISTS always_tax_exigible BOOL""",
    )
    # 1. Set always_tax_exigible = False if record.is_invoice(True) is True
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE account_move
        SET always_tax_exigible = FALSE
        WHERE move_type IN ('out_invoice', 'out_refund', 'in_refund',
            'in_invoice', 'out_receipt', 'in_receipt')""",
    )
    # 2. Set always_tax_exigible = False
    #    if record._collect_tax_cash_basis_values() is True
    #    Which it happens only if [(2.1) AND (2.2 OR 2.3 OR 2.4)] is True
    # 2.1 If invoice is not multiple involved currencies
    # 2.2 If any(line.account_internal_type in ('receivable', 'payable')
    # 2.3 If any(line.tax_line_id.tax_exigibility == 'on_payment')
    # 2.4 If any(line.tax_ids.flatten_taxes_hierarchy().mapped('tax_exigibility'))
    openupgrade.logged_query(
        env.cr,
        """
        WITH move_currency_rel AS (
            SELECT am.id, aml.currency_id
            FROM account_move am
            JOIN account_move_line aml ON aml.move_id = am.id
            LEFT JOIN account_account aa ON aa.id = aml.account_id
            LEFT JOIN account_account_type aat ON aat.id = aa.user_type_id
            LEFT JOIN account_tax tax ON aml.tax_line_id = tax.id
            LEFT JOIN account_move_line_account_tax_rel aml_tax_rel ON
                aml.id = aml_tax_rel.account_move_line_id
            LEFT JOIN account_tax tax2 ON (
                tax2.id = aml_tax_rel.account_tax_id AND tax2.amount_type != 'group')
            LEFT JOIN account_tax parent_tax ON (
                parent_tax.id = aml_tax_rel.account_tax_id AND parent_tax.amount_type = 'group')
            LEFT JOIN account_tax_filiation_rel tax_fil_rel ON
                tax_fil_rel.parent_tax = parent_tax.id
            LEFT JOIN account_tax tax3 ON (
                tax3.id = tax_fil_rel.child_tax AND tax3.amount_type != 'group')
            WHERE am.always_tax_exigible IS NULL AND (
                aat.type IN ('receivable', 'payable') OR
                tax.tax_exigibility = 'on_payment' OR
                tax2.tax_exigibility = 'on_payment' OR
                tax3.tax_exigibility = 'on_payment')
            GROUP BY am.id, aml.currency_id
        ), sub AS (
            SELECT id
            FROM move_currency_rel
            GROUP BY id
            HAVING count(*) = 1
        )
        UPDATE account_move am
        SET always_tax_exigible = FALSE
        FROM sub
        WHERE sub.id = am.id
        """,
    )
    # 3. Set always_tax_exigible = TRUE otherwise
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE account_move
        SET always_tax_exigible = TRUE
        WHERE always_tax_exigible IS NULL""",
    )


def _fast_fill_account_move_amount_total_in_currency_signed(env):
    openupgrade.logged_query(
        env.cr,
        """
        ALTER TABLE account_move
        ADD COLUMN IF NOT EXISTS amount_total_in_currency_signed NUMERIC""",
    )
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE account_move
        SET amount_total_in_currency_signed =
            CASE
                WHEN move_type = 'entry'
                THEN ABS(amount_total)
                WHEN move_type IN ('in_invoice', 'out_refund', 'in_receipt')
                THEN -amount_total
                ELSE amount_total
            END""",
    )


def _fast_fill_account_move_line_tax_tag_invert(env):
    openupgrade.logged_query(
        env.cr,
        """
        ALTER TABLE account_move_line
        ADD COLUMN IF NOT EXISTS tax_tag_invert BOOL""",
    )
    # 1. Invoices imported from other softwares might only have kept the tags,
    # not the taxes
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE account_move_line aml
        SET tax_tag_invert = sub.tax_tag_invert
        FROM (
            SELECT DISTINCT ON (aml.id) aml.id,
                CASE
                    WHEN tag_rel.account_move_line_id IS NOT NULL
                        AND am.move_type IN ('out_invoice', 'in_refund', 'out_receipt')
                    THEN TRUE
                    ELSE FALSE
                END AS tax_tag_invert
            FROM account_move am
            JOIN account_move_line aml ON am.id = aml.move_id
            LEFT JOIN account_move_line_account_tax_rel tax_rel
                ON aml.id = tax_rel.account_move_line_id
            LEFT JOIN account_account_tag_account_move_line_rel tag_rel
                ON aml.id = tag_rel.account_move_line_id
            WHERE am.move_type = 'entry' AND aml.tax_repartition_line_id IS NULL
                AND tax_rel.account_move_line_id IS NULL
        ) sub
        WHERE sub.id = aml.id""",
    )
    # 2. For invoices with taxes
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE account_move_line aml
        SET tax_tag_invert =
            CASE
                WHEN am.move_type IN ('out_invoice', 'in_refund', 'out_receipt')
                THEN TRUE
                ELSE FALSE
            END
        FROM account_move am
        WHERE am.id = aml.move_id AND am.move_type != 'entry'
            AND aml.tax_tag_invert IS NULL""",
    )
    # 3. For misc operations,
    # cash basis entries and write-offs from the bank reconciliation widget
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE account_move_line aml
        SET tax_tag_invert = sub.tax_tag_invert
        FROM (
            SELECT aml.id,
                CASE
                    WHEN refund_tax.type_tax_use = 'purchase'
                        OR (invoice_tax.type_tax_use = 'sale'
                            AND atpl.refund_tax_id IS NULL)
                    THEN TRUE
                    ELSE FALSE
                END AS tax_tag_invert
            FROM account_move am
            JOIN account_move_line aml ON am.id = aml.move_id
            JOIN account_tax_repartition_line atpl ON aml.tax_repartition_line_id = atpl.id
            LEFT JOIN account_tax refund_tax ON refund_tax.id = atpl.refund_tax_id
            LEFT JOIN account_tax invoice_tax ON invoice_tax.id = atpl.invoice_tax_id
            WHERE am.move_type = 'entry'
        ) sub
        WHERE sub.id = aml.id AND aml.tax_tag_invert IS NULL
        """,
    )
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE account_move_line aml
        SET tax_tag_invert = sub.tax_tag_invert
        FROM (
            SELECT DISTINCT ON (aml.id) aml.id,
                CASE
                    WHEN (tax.type_tax_use = 'purchase' AND (
                            aml.credit != 0 AND aml.credit IS NOT NULL))
                        OR (tax.type_tax_use = 'sale' AND (
                            aml.debit = 0 OR aml.debit IS NULL))
                    THEN TRUE
                    ELSE FALSE
                END AS tax_tag_invert
            FROM account_move am
            JOIN account_move_line aml ON am.id = aml.move_id
            JOIN account_move_line_account_tax_rel tax_rel ON
                aml.id = tax_rel.account_move_line_id
            JOIN account_tax tax ON tax.id = tax_rel.account_tax_id
            WHERE am.move_type = 'entry'
        ) sub
        WHERE sub.id = aml.id AND aml.tax_tag_invert IS NULL""",
    )


def _create_account_payment_method_line(env):
    # Create account_payment_method_line table
    sql.create_model_table(
        env.cr,
        "account_payment_method_line",
        columns=[
            ("name", "varchar", ""),
            ("sequence", "integer", ""),
            ("payment_method_id", "integer", ""),
            ("payment_account_id", "integer", ""),
            ("journal_id", "integer", ""),
            ("create_uid", "integer", ""),
            ("create_date", "timestamp", ""),
            ("write_uid", "integer", ""),
            ("write_date", "timestamp", ""),
        ],
    )
    # Create account payment method lines from account payment methods
    openupgrade.logged_query(
        env.cr,
        """
        INSERT INTO account_payment_method_line (name, sequence,
            payment_method_id, journal_id, create_uid, write_uid,
            create_date, write_date)
        SELECT apm.name, 10, apm.id, aj.id,
            apm.create_uid, apm.write_uid, apm.create_date, apm.write_date
        FROM account_payment_method apm, account_journal aj
        WHERE apm.code = 'manual' AND aj.type IN ('bank', 'cash')
        """,
    )


def _fast_fill_account_payment_payment_method_line_id(env):
    openupgrade.logged_query(
        env.cr,
        """
        ALTER TABLE account_payment
        ADD COLUMN IF NOT EXISTS payment_method_line_id INTEGER""",
    )
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE account_payment ap
        SET payment_method_line_id = apml.id
        FROM account_move am
        JOIN account_payment_method_line apml ON apml.journal_id = am.journal_id
        WHERE ap.move_id = am.id AND ap.payment_method_id = apml.payment_method_id
        """,
    )


def _fill_account_tax_country_id(env):
    openupgrade.logged_query(
        env.cr,
        """
        ALTER TABLE account_tax
        ADD COLUMN IF NOT EXISTS country_id INTEGER
        """,
    )
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE account_tax at
        SET country_id = COALESCE(c.account_fiscal_country_id, p.country_id)
        FROM res_company c
        LEFT JOIN res_partner p ON p.id = c.partner_id
        WHERE c.id = at.company_id
        """,
    )


def _fill_res_company_account_journal_payment_accounts(env):
    # account_journal_payment_credit_account_id
    openupgrade.logged_query(
        env.cr,
        """
        ALTER TABLE res_company
        ADD COLUMN IF NOT EXISTS account_journal_payment_credit_account_id INTEGER
        """,
    )
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE res_company c
        SET account_journal_payment_credit_account_id = (
            SELECT aj.payment_credit_account_id
            FROM account_journal aj
            WHERE aj.company_id = c.id AND aj.type IN ('bank', 'cash')
                AND aj.payment_credit_account_id IS NOT NULL
            LIMIT 1)""",
    )
    # account_journal_payment_debit_account_id
    openupgrade.logged_query(
        env.cr,
        """
        ALTER TABLE res_company
        ADD COLUMN IF NOT EXISTS account_journal_payment_debit_account_id INTEGER
        """,
    )
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE res_company c
        SET account_journal_payment_debit_account_id = (
            SELECT aj.payment_debit_account_id
            FROM account_journal aj
            WHERE aj.company_id = c.id AND aj.type IN ('bank', 'cash')
                AND aj.payment_debit_account_id IS NOT NULL
            LIMIT 1)""",
    )


def _fast_create_account_payment_outstanding_account_id(env):
    # avoid being filled when loading the module
    openupgrade.logged_query(
        env.cr,
        """
        ALTER TABLE account_payment
        ADD COLUMN IF NOT EXISTS outstanding_account_id INTEGER""",
    )


def _remove_table_constraints(env):
    openupgrade.remove_tables_fks(
        env.cr,
        [
            "account_journal_inbound_payment_method_rel",
            "account_journal_outbound_payment_method_rel",
        ],
    )
    openupgrade.lift_constraints(env.cr, "account_journal", "payment_credit_account_id")
    openupgrade.lift_constraints(env.cr, "account_journal", "payment_debit_account_id")
    openupgrade.lift_constraints(env.cr, "res_company", "account_tax_fiscal_country_id")
    openupgrade.delete_sql_constraint_safely(
        env, "account", "account_journal", "code_company_uniq"
    )


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.set_xml_ids_noupdate_value(
        env, "account", ["action_account_resequence"], True
    )
    openupgrade.rename_fields(env, _renamed_fields)
    openupgrade.delete_records_safely_by_xml_id(env, ["account.invoice_send"])
    switch_payment_tolerance_param_value(env)
    _convert_field_to_html(env)
    _fast_fill_account_move_always_tax_exigible(env)
    _fast_fill_account_move_amount_total_in_currency_signed(env)
    _fast_fill_account_move_line_tax_tag_invert(env)
    _create_account_payment_method_line(env)
    _fast_fill_account_payment_payment_method_line_id(env)
    _fill_res_company_account_journal_payment_accounts(env)
    _fast_create_account_payment_outstanding_account_id(env)
    _fill_account_tax_country_id(env)
    _remove_table_constraints(env)
