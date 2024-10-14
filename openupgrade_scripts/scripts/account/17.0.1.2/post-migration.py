# Copyright 2024 Viindoo Technology Joint Stock Company (Viindoo)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade

_deleted_xml_records = [
    "account.account_payment_term_2months",
    "account.tax_group_taxes",
    "account.account_invoice_send_rule_group_invoice",
    "account.sequence_reconcile_seq",
]


def _am_update_invoice_pdf_report_file(env):
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE ir_attachment ia
        SET res_field = 'invoice_pdf_report_file',
            res_id = am.id
        FROM account_move am
        WHERE am.message_main_attachment_id = ia.id
        """,
    )


def _onboarding_state_migration(env):
    """
    Following pr: https://github.com/odoo/odoo/pull/104223/
    """
    env.cr.execute(
        """
        SELECT id, account_onboarding_create_invoice_state_flag,
        account_onboarding_invoice_layout_state,
        account_onboarding_sale_tax_state, account_setup_bank_data_state,
        account_setup_bill_state, account_setup_coa_state, account_setup_fy_data_state,
        account_setup_taxes_state FROM res_company
        """
    )
    for (
        company_id,
        account_onboarding_create_invoice_state_flag,
        account_onboarding_invoice_layout_state,
        account_onboarding_sale_tax_state,
        account_setup_bank_data_state,
        account_setup_bill_state,
        account_setup_coa_state,
        account_setup_fy_data_state,
        account_setup_taxes_state,
    ) in env.cr.fetchall():
        OnboardingStep = env["onboarding.onboarding.step"].with_company(company_id)
        company = env["res.company"].browse(company_id)
        if company.street and company.street.strip():
            # Same behaviour for this base setup company data in v16
            # Check method 'action_save_onboarding_company_step' in v16
            # Note in v17 you only need to save it then it will be done
            OnboardingStep.action_validate_step(
                "account.onboarding_onboarding_step_company_data"
            )
        if account_onboarding_create_invoice_state_flag:
            step = env.ref(
                "account.onboarding_onboarding_step_create_invoice",
                raise_if_not_found=False,
            )
            if step and step.current_step_state == "not_done":
                if env["account.move"].search(
                    [
                        ("company_id", "=", company_id),
                        ("move_type", "=", "out_invoice"),
                    ],
                    limit=1,
                ):
                    step.action_set_just_done()
        if account_onboarding_invoice_layout_state in ("just_done", "done"):
            step = env.ref(
                "account.onboarding_onboarding_step_base_document_layout",
                raise_if_not_found=False,
            )
            if step:
                step.with_company(company_id).action_set_just_done()
        if account_onboarding_sale_tax_state in ("just_done", "done"):
            OnboardingStep.action_validate_step(
                "account.onboarding_onboarding_step_sales_tax"
            )
        if account_setup_bank_data_state in ("just_done", "done"):
            OnboardingStep.action_validate_step(
                "account.onboarding_onboarding_step_bank_account"
            )
        if account_setup_bill_state in ("just_done", "done"):
            OnboardingStep.action_validate_step(
                "account.onboarding_onboarding_step_setup_bill"
            )
        if account_setup_coa_state in ("just_done", "done"):
            OnboardingStep.action_validate_step(
                "account.onboarding_onboarding_step_chart_of_accounts"
            )
        if account_setup_fy_data_state in ("just_done", "done"):
            OnboardingStep.action_validate_step(
                "account.onboarding_onboarding_step_fiscal_year"
            )
        if account_setup_taxes_state in ("just_done", "done"):
            OnboardingStep.action_validate_step(
                "account.onboarding_onboarding_step_default_taxes"
            )


def _account_payment_term_migration(env):
    """
    In post we will update the value_amount field
    to respect v17 to ensure total percentage will not
    exceed 100% of not <100%
    In v16, the payment term might have some cases like
    -Case 1
        line 1: value - balance, value_amount - 0.0
        line 2: value - percent, value_amount - 50
        line 3: value - percent, value_amount - 45
    -Case 2
        line 1: value - balance, value_amount - 0.0
        line 2: value - percent, value_amount - 100
    NOTE: in pre we already convert value_amount of balance to 100.0 %
    AFTER migration: line 1 of case 1 will have 'value_amount' is 5%
    line 2 of case 2 will have 'value_amount' is 100% while line 2 is 0.0%
    """
    payment_terms = (
        env["account.payment.term"].with_context(active_test=False).search([])
    )
    for term in payment_terms:
        term_lines = term.line_ids.filtered(lambda line: line.value == "percent")
        value_amount_total = sum(term_lines.mapped("value_amount"))
        if value_amount_total and value_amount_total > 100.0:
            term_lines_with_100_percentage = term_lines.filtered(
                lambda line: line.value_amount == 100
            )
            term_lines_below_100_percentage = term_lines.filtered(
                lambda line: line.value_amount < 100
            )
            if len(term_lines_with_100_percentage) > 1:
                (
                    term_lines_with_100_percentage - term_lines_with_100_percentage[0]
                ).write(
                    {
                        "value_amount": 0.0,
                    }
                )
            if term_lines_below_100_percentage:
                remaining_line = term_lines - term_lines_below_100_percentage
                if remaining_line:
                    remaining_line.write(
                        {
                            "value_amount": 100
                            - sum(
                                term_lines_below_100_percentage.mapped("value_amount")
                            )
                        }
                    )


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.load_data(env, "account", "17.0.1.2/noupdate_changes.xml")
    openupgrade.delete_records_safely_by_xml_id(
        env,
        _deleted_xml_records,
    )
    _am_update_invoice_pdf_report_file(env)
    _onboarding_state_migration(env)
    _account_payment_term_migration(env)
