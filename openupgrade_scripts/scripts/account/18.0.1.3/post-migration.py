# Copyright 2025 ForgeFlow S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from openupgradelib import openupgrade, openupgrade_180


def handle_lock_dates(env):
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE res_company
        SET sale_lock_date = period_lock_date, purchase_lock_date = period_lock_date
        WHERE period_lock_date IS NOT NULL""",
    )
    env.cr.execute(
        f"""
        SELECT state
        FROM {openupgrade.get_legacy_name("ir_module_module")}
        WHERE name = 'account_lock'
        """
    )
    row = env.cr.fetchone()
    account_lock_state = row and row[0] or ""
    if account_lock_state == "installed":
        openupgrade.logged_query(
            env.cr,
            """
            UPDATE res_company
            SET hard_lock_date = fiscalyear_lock_date
            WHERE fiscalyear_lock_date IS NOT NULL""",
        )


def link_payments_to_moves(env):
    openupgrade.logged_query(
        env.cr,
        """
        INSERT INTO account_move__account_payment (invoice_id, payment_id)
        SELECT am.id, ap.id
        FROM account_payment ap
        JOIN account_move am ON ap.move_id = am.id
        """,
    )


def convert_company_dependent(env):
    openupgrade_180.convert_company_dependent(
        env, "account.cash.rounding", "loss_account_id"
    )
    openupgrade_180.convert_company_dependent(
        env, "account.cash.rounding", "profit_account_id"
    )
    openupgrade_180.convert_company_dependent(
        env, "product.category", "property_account_expense_categ_id"
    )
    openupgrade_180.convert_company_dependent(
        env, "product.category", "property_account_income_categ_id"
    )
    openupgrade_180.convert_company_dependent(
        env, "product.template", "property_account_expense_id"
    )
    openupgrade_180.convert_company_dependent(
        env, "product.template", "property_account_income_id"
    )
    openupgrade_180.convert_company_dependent(env, "res.partner", "credit_limit")
    openupgrade_180.convert_company_dependent(
        env, "res.partner", "property_account_payable_id"
    )
    openupgrade_180.convert_company_dependent(
        env, "res.partner", "property_account_position_id"
    )
    openupgrade_180.convert_company_dependent(
        env, "res.partner", "property_account_receivable_id"
    )
    openupgrade_180.convert_company_dependent(
        env, "res.partner", "property_payment_term_id"
    )
    openupgrade_180.convert_company_dependent(
        env, "res.partner", "property_supplier_payment_term_id"
    )
    openupgrade_180.convert_company_dependent(env, "res.partner", "trust")


def fill_res_partner_property_x_payment_method_line_id(env):
    if not openupgrade.column_exists(
        env.cr, "account_move", "preferred_payment_method_id"
    ):
        return
    # having account_check_printing module
    env.cr.execute(
        """
        SELECT id FROM ir_model_fields
        WHERE model = 'res.partner'
            AND name = 'property_payment_method_id'"""
    )
    old_field_id = env.cr.fetchone()[0]
    openupgrade.logged_query(
        env.cr,
        f"""
        UPDATE res_partner
        SET property_outbound_payment_method_line_id=ir_property_by_company.value
        FROM (
            SELECT
            SPLIT_PART(ip.res_id, ',', 2)::integer res_id,
            JSON_OBJECT_AGG(ip.company_id, sub.id) AS "value"
            FROM ir_property ip
            JOIN LATERAL (
                SELECT *
                FROM account_payment_method_line apml
                WHERE apml.payment_method_id = SPLIT_PART(
                    ip.value_reference, ',', 2)::integer
                LIMIT 1
            ) as sub ON TRUE
            WHERE ip.fields_id={old_field_id} AND ip.res_id IS NOT NULL
                AND ip.company_id IS NOT NULL AND sub.id IS NOT NULL
            GROUP BY res_id
        ) ir_property_by_company
        WHERE res_partner.id=ir_property_by_company.res_id
        """,
    )
    env.cr.execute(
        f"""
        SELECT ip.company_id, sub.id
        FROM ir_property ip
        JOIN LATERAL (
            SELECT *
            FROM account_payment_method_line apml
            WHERE apml.payment_method_id = SPLIT_PART(
                ip.value_reference, ',', 2)::integer
            LIMIT 1
        ) as sub ON TRUE
        WHERE ip.fields_id={old_field_id} AND res_id IS NULL AND sub.id IS NOT NULL
        """
    )
    for company_id, value in env.cr.fetchall():
        env["ir.default"].set(
            "res.partner",
            "property_outbound_payment_method_line_id",
            value,
            company_id=company_id,
        )


def account_account_code_fields(env):
    """
    Fill account.account#code_store from company_id and code
    """
    env.cr.execute(
        """
        UPDATE account_account aa
        SET code_store=json_build_object(split_part(rc.parent_path, '/', 1), aa.code)
        FROM res_company rc
        WHERE aa.company_id = rc.id
        """
    )


def _handle_outstanding_accounts(env):
    """On version 17, the outstanding accounts were handled with 2 fields on each
    res.company.

    Now, they are handled putting specific XML-IDs on them, so we should create that
    identifiers on the previous referenced accounts.

    Besides, now Odoo doesn't generate journal entries by default, unless there's an
    outstanding account put on the payment method line on the journals, so let's keep
    the previous behavior setting the same outstanding accounts on the lines that have
    it empty.
    """
    IMD = env["ir.model.data"]
    for column in [
        "account_journal_payment_debit_account_id",
        "account_journal_payment_credit_account_id",
    ]:
        env.cr.execute(
            f"SELECT id, {column} FROM res_company WHERE {column} IS NOT NULL"
        )
        for company_id, account_id in env.cr.fetchall():
            name = f"{company_id}_{column}"
            if not IMD.search([("module", "=", "account"), ("name", "=", name)]):
                IMD.create(
                    {
                        "module": "account",
                        "name": name,
                        "model": "account.account",
                        "res_id": account_id,
                        "noupdate": True,
                    }
                )
            # Fill the outstanding account on journals
            payment_type = (
                "inbound"
                if column == "account_journal_payment_debit_account_id"
                else "outbound"
            )
            openupgrade.logged_query(
                env.cr,
                f"""UPDATE account_payment_method_line apml
                SET payment_account_id = {account_id}
                FROM account_journal aj, account_payment_method apm
                WHERE aj.id = apml.journal_id
                    AND apm.id = apml.payment_method_id
                    AND aj.type IN ('bank', 'cash')
                    AND apm.payment_type = '{payment_type}'
                    AND apml.payment_account_id IS NULL
                    AND aj.company_id = {company_id}
                """,
            )


def _create_batch_payment_sequence(env):
    """Creates a Batch Payment Number Sequence for every company that does not
    have one yet. This covers companies that existed before the ``account``
    module was installed.

    From https://github.com/odoo/odoo/pull/273905.
    The sequence is now created when installing the module, but still isn't when
    migrating from a lower version.
    This causes errors after migration when making a batch payment.
    """
    to_create_seqs = env["res.company"].search(
        [("batch_payment_sequence_id", "=", False)]
    )
    to_create_seqs._create_batch_payment_sequence()


def fix_payment_paid_state(env):
    """Set 'paid' on the payments that fill_account_payment left as 'in_process'.

    It reads the payment's own move, whose payment_state is always 'not_paid'
    below v18 as it is only computed for invoices, so every posted payment ends
    up 'in_process'. Apply the two conditions of account.payment._compute_state.
    """
    # liquidity line fully reconciled, or on a non reconcilable account
    openupgrade.logged_query(
        env.cr,
        """
        WITH liquidity AS (
            SELECT ap.id AS payment_id,
                SUM(aml.amount_residual) AS residual,
                BOOL_OR(aa.reconcile) AS reconcilable,
                cur.rounding AS rounding
            FROM account_payment ap
            JOIN account_move am ON am.id = ap.move_id
            JOIN res_company rc ON rc.id = am.company_id
            JOIN res_currency cur ON cur.id = rc.currency_id
            JOIN account_journal aj ON aj.id = ap.journal_id
            JOIN account_move_line aml ON aml.move_id = am.id
            JOIN account_account aa ON aa.id = aml.account_id
            LEFT JOIN account_payment_method_line apml
                ON apml.id = ap.payment_method_line_id
            WHERE ap.state = 'in_process'
                AND (
                    aml.account_id = aj.default_account_id
                    OR aml.account_id = ap.outstanding_account_id
                    OR aml.account_id = apml.payment_account_id
                    OR aml.account_id IN (
                        SELECT payment_account_id
                        FROM account_payment_method_line
                        WHERE journal_id = ap.journal_id
                            AND payment_account_id IS NOT NULL
                    )
                )
            GROUP BY ap.id, cur.rounding
        )
        UPDATE account_payment ap
        SET state = 'paid'
        FROM liquidity
        WHERE ap.id = liquidity.payment_id
            AND (
                NOT liquidity.reconcilable
                OR ABS(liquidity.residual) < liquidity.rounding / 2
            )
        """,
    )
    # all the reconciled invoices, or all the reconciled bills, are paid
    openupgrade.logged_query(
        env.cr,
        """
        WITH reconciled AS (
            SELECT DISTINCT ap.id AS payment_id, inv.id AS invoice_id,
                inv.move_type, inv.payment_state
            FROM account_payment ap
            JOIN account_move am ON am.id = ap.move_id
            JOIN account_move_line aml ON aml.move_id = am.id
            JOIN account_account aa ON aa.id = aml.account_id
            JOIN account_partial_reconcile apr
                ON apr.debit_move_id = aml.id OR apr.credit_move_id = aml.id
            JOIN account_move_line counterpart
                ON (apr.debit_move_id = counterpart.id
                    OR apr.credit_move_id = counterpart.id)
                AND counterpart.id != aml.id
            JOIN account_move inv ON inv.id = counterpart.move_id
            WHERE ap.state = 'in_process'
                AND aa.account_type IN ('asset_receivable', 'liability_payable')
                AND inv.move_type IN (
                    'out_invoice', 'out_refund', 'out_receipt',
                    'in_invoice', 'in_refund', 'in_receipt'
                )
        ), counts AS (
            SELECT payment_id,
                COUNT(*) FILTER (WHERE move_type IN (
                    'out_invoice', 'out_refund', 'out_receipt')) AS invoices,
                COUNT(*) FILTER (WHERE move_type IN (
                    'out_invoice', 'out_refund', 'out_receipt')
                    AND payment_state = 'paid') AS paid_invoices,
                COUNT(*) FILTER (WHERE move_type IN (
                    'in_invoice', 'in_refund', 'in_receipt')) AS bills,
                COUNT(*) FILTER (WHERE move_type IN (
                    'in_invoice', 'in_refund', 'in_receipt')
                    AND payment_state = 'paid') AS paid_bills
            FROM reconciled
            GROUP BY payment_id
        )
        UPDATE account_payment ap
        SET state = 'paid'
        FROM counts
        WHERE ap.id = counts.payment_id
            AND ap.state = 'in_process'
            AND (
                (counts.invoices > 0 AND counts.invoices = counts.paid_invoices)
                OR (counts.bills > 0 AND counts.bills = counts.paid_bills)
            )
        """,
    )


@openupgrade.migrate()
def migrate(env, version):
    handle_lock_dates(env)
    link_payments_to_moves(env)
    account_account_code_fields(env)
    _handle_outstanding_accounts(env)
    _create_batch_payment_sequence(env)
    openupgrade.m2o_to_x2m(
        env.cr, env["account.account"], "account_account", "company_ids", "company_id"
    )
    convert_company_dependent(env)
    fill_res_partner_property_x_payment_method_line_id(env)
    fix_payment_paid_state(env)
    openupgrade.load_data(env, "account", "18.0.1.3/noupdate_changes.xml")
    openupgrade.delete_record_translations(
        env.cr, "account", ["email_template_edi_invoice"]
    )
    openupgrade.delete_record_translations(
        env.cr,
        "account",
        ["account_payment_method_manual_in", "account_payment_method_manual_out"],
        ["name"],
    )
    openupgrade.delete_record_translations(
        env.cr,
        "account",
        [
            "onboarding_onboarding_step_chart_of_accounts",
            "onboarding_onboarding_step_company_data",
            "onboarding_onboarding_step_fiscal_year",
        ],
        ["title"],
    )
    openupgrade.delete_records_safely_by_xml_id(
        env,
        [
            "account.default_followup_trust",
            "account.account_move_send_rule_group_invoice",
            "account.account_root_comp_rule",
            "count.onboarding_onboarding_account_invoice",
            "account.onboarding_onboarding_step_bank_account",
            "account.onboarding_onboarding_step_create_invoice",
            "account.onboarding_onboarding_step_default_taxes",
            "account.onboarding_onboarding_step_setup_bill",
        ],
    )
