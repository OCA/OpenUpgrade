# Copyright 2021 ForgeFlow S.L.  <https://www.forgeflow.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
import logging

from openupgradelib import openupgrade

from odoo.tools.translate import _

_logger = logging.getLogger(__name__)


def _create_hooks(env):
    def _check_fiscalyear_lock_date(self):
        return True

    def _check_tax_lock_date(self):
        return True

    def _check_reconciliation(self):
        return True

    # create hooks
    _check_fiscalyear_lock_date._original_method = type(
        env["account.move"]
    )._check_fiscalyear_lock_date
    type(env["account.move"])._check_fiscalyear_lock_date = _check_fiscalyear_lock_date
    _check_tax_lock_date._original_method = type(
        env["account.move.line"]
    )._check_tax_lock_date
    type(env["account.move.line"])._check_tax_lock_date = _check_tax_lock_date
    _check_reconciliation._original_method = type(
        env["account.move.line"]
    )._check_reconciliation
    type(env["account.move.line"])._check_reconciliation = _check_reconciliation


def _delete_hooks(env):
    # delete hooks
    type(env["account.move"])._check_fiscalyear_lock_date = type(
        env["account.move"]
    )._check_fiscalyear_lock_date._original_method
    type(env["account.move.line"])._check_tax_lock_date = type(
        env["account.move.line"]
    )._check_tax_lock_date._original_method
    type(env["account.move.line"])._check_reconciliation = type(
        env["account.move.line"]
    )._check_reconciliation._original_method


def fill_account_journal_posted_before(env):
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE account_move
        SET posted_before = TRUE
        WHERE state = 'posted'""",
    )


def fill_code_prefix_end_field(env):
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE account_group
        SET code_prefix_end = code_prefix_start
        """,
    )


def fill_default_account_id_field(env):
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE account_journal
        SET default_account_id = {0}
        WHERE {0} = {1} OR ({0} IS NOT NULL AND {1} IS NULL);
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
        UPDATE account_move_line aml
        SET payment_id = am.payment_id
        FROM account_move am
        WHERE am.id = aml.move_id AND am.payment_id IS NOT NULL
            AND aml.payment_id IS NULL
        """,
    )
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE account_move_line aml
        SET statement_line_id = am.statement_line_id
        FROM account_move am
        WHERE am.id = aml.move_id AND am.statement_line_id IS NOT NULL
            AND aml.statement_line_id IS NULL
        """,
    )


def fill_partial_reconcile_debit_and_credit_amounts(env):
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE account_partial_reconcile
        SET debit_amount_currency = COALESCE(NULLIF(amount_currency, 0.0), amount),
            debit_currency_id = COALESCE(currency_id, debit_currency_id)
        WHERE debit_amount_currency IS NULL
       """,
    )
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE account_partial_reconcile
        SET credit_amount_currency = COALESCE(NULLIF(amount_currency, 0.0), amount),
            credit_currency_id = COALESCE(currency_id, credit_currency_id)
        WHERE credit_amount_currency IS NULL
       """,
    )


def create_account_reconcile_model_lines(env):
    openupgrade.logged_query(
        env.cr,
        """
        INSERT INTO account_reconcile_model_line (model_id, company_id,
            sequence, account_id, journal_id, label, amount_type,
            force_tax_included, amount, amount_string, analytic_account_id,
            create_uid, create_date, write_uid, write_date)
        SELECT id, company_id, 10, account_id, journal_id, label,
            amount_type, force_tax_included,
            CASE WHEN amount_type = 'regex' THEN 0 ELSE amount END as amount,
            CASE WHEN amount_type = 'regex' THEN amount_from_label_regex
                ELSE amount || '' END as amount_string,
            analytic_account_id, create_uid, create_date, write_uid, write_date
        FROM (
            SELECT arm.* FROM account_reconcile_model arm
            LEFT JOIN ir_model_data imd ON (
                imd.model = 'account.reconcile.model' AND imd.res_id = arm.id)
            WHERE imd.id IS NULL) arm1
        WHERE rule_type != 'invoice_matching' OR (rule_type = 'invoice_matching'
            AND match_total_amount AND match_total_amount_param < 100.0)
        UNION ALL
        SELECT id, company_id, 20, second_account_id, second_journal_id,
            second_label, second_amount_type, force_second_tax_included,
            CASE WHEN second_amount_type = 'regex' THEN 0
                ELSE second_amount END as amount,
            CASE WHEN second_amount_type = 'regex' THEN second_amount_from_label_regex
                ELSE second_amount || '' END as amount_string,
            second_analytic_account_id, create_uid, create_date, write_uid, write_date
        FROM (
            SELECT arm.* FROM account_reconcile_model arm
            LEFT JOIN ir_model_data imd ON (
                imd.model = 'account.reconcile.model' AND imd.res_id = arm.id)
            WHERE imd.id IS NULL) arm2
        WHERE has_second_line AND (rule_type != 'invoice_matching' OR (
            rule_type = 'invoice_matching' AND match_total_amount
            AND match_total_amount_param < 100.0))
        ORDER BY id""",
    )
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE account_reconcile_model_analytic_tag_rel rel
        SET account_reconcile_model_line_id = arml.id
        FROM account_reconcile_model_line arml
        WHERE arml.model_id = rel.account_reconcile_model_id""",
    )
    openupgrade.logged_query(
        env.cr,
        """
        DELETE FROM account_reconcile_model_analytic_tag_rel
        WHERE account_reconcile_model_line_id IS NULL""",
    )
    openupgrade.logged_query(
        env.cr,
        """
        INSERT INTO account_reconcile_model_analytic_tag_rel (
            account_reconcile_model_line_id, account_analytic_tag_id)
        SELECT arml.id, rel.account_analytic_tag_id
        FROM account_reconcile_model_second_analytic_tag_rel rel
        JOIN account_reconcile_model_line arml
            ON rel.account_reconcile_model_id = arml.model_id""",
    )
    openupgrade.logged_query(
        env.cr,
        """
        INSERT INTO account_reconcile_model_line_account_tax_rel (
            account_reconcile_model_line_id, account_tax_id)
        SELECT arml.id, rel.account_tax_id
        FROM account_reconcile_model_account_tax_rel rel
        JOIN account_reconcile_model_line arml
            ON rel.account_reconcile_model_id = arml.model_id""",
    )
    openupgrade.logged_query(
        env.cr,
        """
        INSERT INTO account_reconcile_model_line_account_tax_rel (
            account_reconcile_model_line_id, account_tax_id)
        SELECT arml.id, rel.account_tax_id
        FROM account_reconcile_model_account_tax_bis_rel rel
        JOIN account_reconcile_model_line arml
            ON rel.account_reconcile_model_id = arml.model_id""",
    )


def create_account_reconcile_model_template_lines(env):
    openupgrade.logged_query(
        env.cr,
        """
        INSERT INTO account_reconcile_model_line_template (model_id,
            sequence, account_id, label, amount_type,
            force_tax_included, amount_string,
            create_uid, create_date, write_uid, write_date)
        SELECT id, 10, account_id, label,
            amount_type, force_tax_included,
            CASE WHEN amount_type = 'regex' THEN amount_from_label_regex
                ELSE amount::varchar END as amount_string,
            create_uid, create_date, write_uid, write_date
        FROM (
            SELECT armt.* FROM account_reconcile_model_template armt
            LEFT JOIN ir_model_data imd ON (
                imd.model = 'account.reconcile.model.template'
                    AND imd.res_id = armt.id)
            WHERE imd.id IS NULL) armt1
        WHERE rule_type != 'invoice_matching' OR (rule_type = 'invoice_matching'
            AND match_total_amount AND match_total_amount_param < 100.0)
        UNION ALL
        SELECT id, 20, second_account_id,
            second_label, second_amount_type, force_second_tax_included,
            CASE WHEN second_amount_type = 'regex' THEN second_amount_from_label_regex
                ELSE second_amount::varchar END as amount_string,
            create_uid, create_date, write_uid, write_date
        FROM (
            SELECT armt.* FROM account_reconcile_model_template armt
            LEFT JOIN ir_model_data imd ON (
                imd.model = 'account.reconcile.model.template'
                    AND imd.res_id = armt.id)
            WHERE imd.id IS NULL) armt2
        WHERE has_second_line AND (rule_type != 'invoice_matching' OR (
            rule_type = 'invoice_matching' AND match_total_amount
            AND match_total_amount_param < 100.0))
        ORDER BY id""",
    )
    openupgrade.logged_query(
        env.cr,
        """
        INSERT INTO account_reconcile_model_line_template_account_tax_template_rel (
            account_reconcile_model_line_template_id, account_tax_template_id)
        SELECT armlt.id, rel.account_tax_template_id
        FROM account_reconcile_model_template_account_tax_template_rel rel
        JOIN account_reconcile_model_line_template armlt
            ON rel.account_reconcile_model_template_id = armlt.model_id""",
    )
    openupgrade.logged_query(
        env.cr,
        """
        INSERT INTO account_reconcile_model_line_template_account_tax_template_rel (
            account_reconcile_model_line_template_id, account_tax_template_id)
        SELECT armlt.id, rel.account_tax_template_id
        FROM account_reconcile_model_tmpl_account_tax_bis_rel rel
        JOIN account_reconcile_model_line_template armlt
            ON rel.account_reconcile_model_template_id = armlt.model_id""",
    )


def create_account_tax_report_lines(env):
    openupgrade.logged_query(
        env.cr,
        """
        ALTER TABLE account_tax_report
        ADD COLUMN root_line_id integer""",
    )
    openupgrade.logged_query(
        env.cr,
        """
        INSERT INTO account_tax_report (name, country_id, root_line_id,
            create_uid, create_date, write_uid, write_date)
        SELECT name, country_id, id, create_uid, create_date, write_uid, write_date
        FROM account_tax_report_line
        WHERE parent_id IS NULL
        """,
    )
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE account_tax_report_line atrl
        SET report_id = atr.id
        FROM account_tax_report atr
        WHERE atr.root_line_id = atrl.id
        """,
    )
    while True:
        openupgrade.logged_query(
            env.cr,
            """
            UPDATE account_tax_report_line atrl
            SET report_id = atrl2.report_id
            FROM account_tax_report_line atrl2
            WHERE atrl.parent_id = atrl2.id AND atrl.report_id IS NULL
            RETURNING atrl.id""",
        )
        if not env.cr.fetchone():
            break


def post_statements_with_unreconciled_lines(env):
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE account_bank_statement bst
        SET state = 'posted'
        FROM account_bank_statement_line bstl
        WHERE bst.state = 'confirm' AND bstl.statement_id = bst.id
            AND bstl.is_reconciled IS DISTINCT FROM TRUE
        """,
    )


def pass_bank_statement_line_note_to_journal_entry_narration(env):
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE account_move am
        SET narration = CASE
            WHEN char_length(COALESCE(am.narration, '')) = 0 THEN absl.note
            ELSE am.narration || ' ' || absl.note END
        FROM account_bank_statement_line absl
        WHERE absl.move_id = am.id AND char_length(COALESCE(absl.note, '')) > 0
        """,
    )


def pass_payment_to_journal_entry_narration(env):
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE account_move am
        SET narration = CASE
            WHEN char_length(COALESCE(am.narration, '')) = 0 THEN ap.communication
            ELSE am.narration || ' ' || ap.communication END
        FROM account_payment ap
        WHERE ap.move_id = am.id AND char_length(COALESCE(ap.communication, '')) > 0
        """,
    )


def fill_company_account_cash_basis_base_account_id(env):
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE account_chart_template chart
        SET property_cash_basis_base_account_id = att.cash_basis_base_account_id
        FROM account_tax_template att
        WHERE att.chart_template_id = chart.id
            AND att.cash_basis_base_account_id IS NOT NULL
        """,
    )
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE res_company rc
        SET account_cash_basis_base_account_id = at.cash_basis_base_account_id
        FROM account_tax at
        WHERE at.company_id = rc.id
            AND at.cash_basis_base_account_id IS NOT NULL
        """,
    )


def fill_company_account_journal_suspense_account_id(env):
    companies = env["res.company"].search([("chart_template_id", "!=", False)])
    for company in companies:
        chart = company.chart_template_id
        account = chart._create_liquidity_journal_suspense_account(
            company, chart.code_digits
        )
        company.account_journal_suspense_account_id = account
    journals = (
        env["account.journal"]
        .with_context(active_test=False)
        .search([("type", "in", ("bank", "cash")), ("company_id", "in", companies.ids)])
    )
    journals._compute_suspense_account_id()


def fill_statement_lines_with_no_move(env):
    stl_dates = {}
    stl_dates_by_company = {}
    env.cr.execute(
        """
        SELECT id, %s, company_id
        FROM account_bank_statement_line
        WHERE move_id IS NULL"""
        % (openupgrade.get_legacy_name("date"),)
    )
    for stl_id, stl_date, stl_company in env.cr.fetchall():
        stl_dates[stl_id] = stl_date
        if stl_company in stl_dates_by_company:
            stl_dates_by_company[stl_company] = min(
                stl_date, stl_dates_by_company[stl_company]
            )
        else:
            stl_dates_by_company[stl_company] = stl_date
    st_lines = env["account.bank.statement.line"].browse(list(stl_dates.keys()))
    for st_line in st_lines.with_context(
        check_move_validity=False, tracking_disable=True
    ):
        move = env["account.move"].create(
            {
                "name": "/",
                "date": stl_dates[st_line.id],
                "statement_line_id": st_line.id,
                "move_type": "entry",
                "journal_id": st_line.statement_id.journal_id.id,
                "company_id": st_line.statement_id.company_id.id,
                "currency_id": st_line.statement_id.journal_id.currency_id.id
                or st_line.statement_id.company_id.currency_id.id,
            }
        )
        st_line.move_id = move
        deprecated_accounts = env["account.account"].search(
            [("deprecated", "=", True), ("company_id", "=", st_line.company_id.id)]
        )
        deprecated_accounts.deprecated = False
        try:
            st_line._synchronize_to_moves(
                [
                    "payment_ref",
                    "amount",
                    "amount_currency",
                    "foreign_currency_id",
                    "currency_id",
                    "partner_id",
                ]
            )
        except Exception as e:
            _logger.error("Failed for statement line with id %s: %s", st_line.id, e)
            raise
        deprecated_accounts.deprecated = True
        to_write = {
            "line_ids": [
                (
                    0,
                    0,
                    st_line._prepare_move_line_default_vals(
                        counterpart_account_id=False
                    )[0],
                )
            ]
        }
        st_line.move_id.with_context(skip_account_move_synchronization=True).write(
            to_write
        )

    openupgrade.logged_query(
        env.cr,
        """
        UPDATE account_move am
        SET partner_bank_id = absl.bank_account_id
        FROM account_bank_statement_line absl
        WHERE am.statement_line_id = absl.id AND am.partner_bank_id IS NULL
            AND absl.bank_account_id IS NOT NULL""",
    )


def fill_account_journal_payment_credit_debit_account_id(env):
    journals = (
        env["account.journal"]
        .with_context(active_test=False)
        .search([("type", "in", ("bank", "cash"))])
    )
    current_assets_type = env.ref("account.data_account_type_current_assets")
    for journal in journals:
        random_account = env["account.account"].search(
            [("company_id", "=", journal.company_id.id)], limit=1
        )
        digits = len(random_account.code) if random_account else 6
        if journal.type == "bank":
            liquidity_account_prefix = journal.company_id.bank_account_code_prefix or ""
        else:
            liquidity_account_prefix = (
                journal.company_id.cash_account_code_prefix
                or journal.company_id.bank_account_code_prefix
                or ""
            )
        journal.payment_debit_account_id = env["account.account"].create(
            {
                "name": _("Outstanding Receipts"),
                "code": env["account.account"]._search_new_account_code(
                    journal.company_id, digits, liquidity_account_prefix
                ),
                "reconcile": True,
                "user_type_id": current_assets_type.id,
                "company_id": journal.company_id.id,
            }
        )
        journal.payment_credit_account_id = (
            env["account.account"]
            .create(
                {
                    "name": _("Outstanding Payments"),
                    "code": env["account.account"]._search_new_account_code(
                        journal.company_id, digits, liquidity_account_prefix
                    ),
                    "reconcile": True,
                    "user_type_id": current_assets_type.id,
                    "company_id": journal.company_id.id,
                }
            )
            .id
        )


def create_new_counterpart_account_payment_transfer(env):
    # Create new counterpart payment with account payment transfer
    openupgrade.logged_query(
        env.cr,
        """
        INSERT INTO account_payment (move_id, is_internal_transfer, partner_type,
            payment_type,
            amount, currency_id,
            destination_account_id, partner_id,
            create_uid, create_date, write_uid, write_date)
        SELECT move.id, true, ap.partner_type,
            CASE
            WHEN journal.id = ap.destination_journal_id THEN 'inbound' ELSE 'outbound'
            END,
            ap.amount, ap.currency_id,
            ap.destination_account_id, ap.partner_id,
            ap.create_uid, ap.create_date, ap.write_uid, ap.write_date
        FROM account_payment ap
        JOIN account_move move
            ON (move.payment_id = ap.id AND move.id != ap.move_id)
        JOIN account_journal journal ON journal.id = move.journal_id
        WHERE ap.payment_type = 'transfer'
        """,
    )


def map_account_payment_transfer(env):
    # map payment_type from transfer to 'inbound'/'outbound'
    # and set is_internal_transfer as true on account payment transfer
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE account_payment ap
        SET is_internal_transfer = true, payment_type = 'outbound'
        WHERE ap.payment_type = 'transfer'
        """,
    )


def fill_account_payment_reconciliation(env):
    openupgrade.logged_query(
        env.cr,
        """
            UPDATE account_payment ap
            SET is_reconciled = True,
                is_matched = True
            FROM res_currency rcur
            WHERE rcur.id = ap.currency_id
                AND ROUND(ap.amount, rcur.decimal_places) = 0
        """,
    )
    openupgrade.logged_query(
        env.cr,
        """
            WITH matched_payments as (
                SELECT ap.id,
                    CASE WHEN aj.default_account_id IS NOT NULL
                            AND bool_or(aj.default_account_id = aml.account_id)
                        THEN TRUE
                    ELSE
                        ROUND(SUM(CASE
                            WHEN aml.account_id in (
                                aj.default_account_id,
                                aj.payment_debit_account_id,
                                aj.payment_credit_account_id
                            ) THEN CASE
                                WHEN rc.currency_id = rcur.id THEN aml.amount_residual
                                ELSE aml.amount_residual_currency END
                            ELSE 0 END
                        ), rcur.decimal_places) = 0
                    END as is_matched,
                    ROUND(
                        SUM(CASE
                            WHEN NOT aa.reconcile THEN 0
                            WHEN aml.account_id not in (
                                aj.default_account_id,
                                aj.payment_debit_account_id,
                                aj.payment_credit_account_id
                            ) THEN CASE
                                WHEN rc.currency_id = rcur.id THEN aml.amount_residual
                                ELSE aml.amount_residual_currency END
                            ELSE 0 END
                        ),
                        rcur.decimal_places
                    ) = 0 as is_reconciled
                FROM account_payment ap
                JOIN account_move am ON am.id = ap.move_id
                JOIN account_move_line aml ON aml.move_id = am.id
                JOIN account_account aa ON aa.id = aml.account_id
                JOIN res_company rc ON rc.id = am.company_id
                JOIN account_journal aj ON aj.id = am.journal_id
                JOIN res_currency rcur ON rcur.id = ap.currency_id
                GROUP BY ap.id, rcur.decimal_places, aj.default_account_id
            )
            UPDATE account_payment ap
            SET is_matched = matched_payments.is_matched,
                is_reconciled = matched_payments.is_reconciled
            FROM matched_payments
            where ap.id = matched_payments.id
        """,
    )


def fill_account_payment_with_no_move(env):
    p_data = {}
    p_dates_by_company = {}
    env.cr.execute(
        """
        SELECT ap.id, ap.%s, ap.%s, ap.%s, ap.state, aj.company_id
        FROM account_payment ap
        JOIN account_journal aj ON ap.%s = aj.id
        WHERE ap.move_id IS NULL
        """
        % (
            openupgrade.get_legacy_name("journal_id"),
            openupgrade.get_legacy_name("name"),
            openupgrade.get_legacy_name("payment_date"),
            openupgrade.get_legacy_name("journal_id"),
        )
    )
    for (
        p_id,
        p_journal_id,
        p_name,
        p_payment_date,
        p_state,
        p_company,
    ) in env.cr.fetchall():
        p_data[p_id] = {
            "journal_id": p_journal_id,
            "name": p_name,
            # Switch to cancel when no linked move, but the payment was validated
            "state": "cancelled" if p_state not in {"draft", "cancelled"} else p_state,
            "payment_date": p_payment_date,
        }
        if p_company in p_dates_by_company:
            p_dates_by_company[p_company] = min(
                p_payment_date, p_dates_by_company[p_company]
            )
        else:
            p_dates_by_company[p_company] = p_payment_date
    payments = env["account.payment"].browse(list(p_data.keys()))
    for payment in payments.with_context(
        check_move_validity=False, tracking_disable=True
    ):
        journal = env["account.journal"].browse(p_data[payment.id]["journal_id"])
        move = env["account.move"].create(
            {
                "name": "/",
                # map old payment's state to move's state:
                # draft -> draft, cancelled -> cancel
                "state": "cancel"
                if p_data[payment.id]["state"] == "cancelled"
                else "draft",
                "date": p_data[payment.id]["payment_date"],
                "payment_id": payment.id,
                "move_type": "entry",
                "journal_id": journal.id,
                "company_id": journal.company_id.id,
                "currency_id": journal.currency_id.id
                or journal.company_id.currency_id.id,
            }
        )
        payment.move_id = move
        deprecated_accounts = env["account.account"].search(
            [("deprecated", "=", True), ("company_id", "=", payment.company_id.id)]
        )
        deprecated_accounts.deprecated = False
        try:
            payment._synchronize_to_moves(
                [
                    "date",
                    "amount",
                    "payment_type",
                    "partner_type",
                    "payment_reference",
                    "is_internal_transfer",
                    "currency_id",
                    "partner_id",
                    "destination_account_id",
                    "partner_bank_id",
                    "journal_id",
                ]
            )
        except Exception as e:
            _logger.error("Failed for payment with id %s: %s", payment.id, e)
            raise
        deprecated_accounts.deprecated = True


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


def fill_account_move_line_amounts(env):
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE account_move_line aml
        SET amount_currency = aml.debit-aml.credit
        FROM account_move am
        JOIN res_company rc ON am.company_id = rc.id
        WHERE aml.currency_id = rc.currency_id AND
            aml.move_id = am.id AND
            aml.debit + aml.credit > 0 AND (
                aml.amount_currency = 0 OR aml.amount_currency IS NULL)""",
    )


def fill_account_move_line_date(env):
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE account_move_line aml
        SET date = COALESCE(am.date, aml.create_date::date)
        FROM account_move am
        WHERE aml.move_id = am.id AND aml.date IS NULL""",
    )


def fill_account_bank_statement_line_reconciliation(env):
    openupgrade.logged_query(
        env.cr,
        """
        WITH absl_residual AS (
            SELECT absl.id,
                CASE
                    WHEN am.to_check
                        AND absl.foreign_currency_id IS NOT NULL
                        THEN -absl.amount_currency
                    WHEN am.to_check THEN -absl.amount
                    ELSE SUM(
                        CASE
                            WHEN aa.reconcile AND aa.id != aj.default_account_id
                                AND aa.id = aj.suspense_account_id
                                THEN aml.amount_residual_currency
                            WHEN aa.id != aj.default_account_id
                                AND aa.id = aj.suspense_account_id
                                THEN aml.amount_currency
                            ELSE 0.
                        END
                    )
                END as amount_residual,
                MIN(CASE
                    WHEN aa.id != aj.default_account_id
                        AND aa.id = aj.suspense_account_id
                        THEN aml.currency_id
                    ELSE NULL END) as suspense_currency_id
            FROM account_bank_statement_line absl
                JOIN account_move am ON am.id = absl.move_id
                JOIN account_move_line aml ON aml.move_id = am.id
                JOIN account_journal aj ON aj.id = am.journal_id
                JOIN account_account aa ON aa.id = aml.account_id
                JOIN res_company rc ON rc.id = aj.company_id
            GROUP BY
                absl.id,
                am.to_check,
                absl.foreign_currency_id,
                absl.amount_currency,
                absl.amount
        )
        UPDATE account_bank_statement_line absl
        SET amount_residual = absl_residual.amount_residual,
            is_reconciled = CASE
                WHEN suspense_currency_id IS NULL THEN TRUE
                ELSE ROUND(absl_residual.amount_residual, rcur.decimal_places) = 0
            END
        FROM absl_residual
            LEFT JOIN res_currency rcur ON rcur.id = absl_residual.suspense_currency_id
        WHERE absl_residual.id = absl.id
        """,
    )


def update_payment_state_partial(env):
    """As the 'Partially paid' didn't exist before, invoices with this condition are
    still marked as 'Not paid', so we should update them as if they were partially paid
    in this new version.
    """
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE account_move
        SET payment_state='partial'
        WHERE move_type IN ('out_invoice', 'out_refund', 'in_invoice', 'in_refund')
            AND amount_residual > 0
            AND amount_residual < amount_total
            AND payment_state != 'partial'
        """,
    )


@openupgrade.migrate()
def migrate(env, version):
    fill_account_journal_posted_before(env)
    fill_code_prefix_end_field(env)
    fill_default_account_id_field(env)
    fill_payment_id_and_statement_line_id_fields(env)
    fill_partial_reconcile_debit_and_credit_amounts(env)
    create_account_reconcile_model_lines(env)
    create_account_reconcile_model_template_lines(env)
    create_account_tax_report_lines(env)
    pass_bank_statement_line_note_to_journal_entry_narration(env)
    pass_payment_to_journal_entry_narration(env)
    fill_company_account_cash_basis_base_account_id(env)
    fill_account_move_line_amounts(env)
    fill_account_move_line_date(env)
    openupgrade.load_data(env.cr, "account", "14.0.1.1/noupdate_changes.xml")
    try_delete_noupdate_records(env)
    _create_hooks(env)
    fill_company_account_journal_suspense_account_id(env)
    fill_statement_lines_with_no_move(env)
    fill_account_journal_payment_credit_debit_account_id(env)
    create_new_counterpart_account_payment_transfer(env)
    map_account_payment_transfer(env)
    fill_account_payment_reconciliation(env)
    fill_account_payment_with_no_move(env)
    fill_account_bank_statement_line_reconciliation(env)
    post_statements_with_unreconciled_lines(env)
    _delete_hooks(env)
    update_payment_state_partial(env)
    openupgrade.delete_record_translations(
        env.cr,
        "account",
        ["email_template_edi_invoice", "mail_template_data_payment_receipt"],
    )
