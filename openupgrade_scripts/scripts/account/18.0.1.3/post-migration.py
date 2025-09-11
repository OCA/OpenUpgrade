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
        UPDATE account_account
        SET code_store=json_build_object(company_id, code)
        """
    )


@openupgrade.migrate()
def migrate(env, version):
    handle_lock_dates(env)
    link_payments_to_moves(env)
    account_account_code_fields(env)
    openupgrade.m2o_to_x2m(
        env.cr, env["account.account"], "account_account", "company_ids", "company_id"
    )
    convert_company_dependent(env)
    fill_res_partner_property_x_payment_method_line_id(env)
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
