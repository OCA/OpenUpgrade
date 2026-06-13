# Copyright 2023 Viindoo - Trịnh Ngọc Hưng
# Copyright 2023-2024 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade

_translations_to_delete = [
    "email_template_edi_credit_note",
    "email_template_edi_invoice",
    "mail_template_data_payment_receipt",
]
_deleted_xml_records = [
    "account.data_account_off_sheet",
    "account.data_account_type_credit_card",
    "account.data_account_type_current_assets",
    "account.data_account_type_current_liabilities",
    "account.data_account_type_depreciation",
    "account.data_account_type_direct_costs",
    "account.data_account_type_equity",
    "account.data_account_type_expenses",
    "account.data_account_type_fixed_assets",
    "account.data_account_type_liquidity",
    "account.data_account_type_non_current_assets",
    "account.data_account_type_non_current_liabilities",
    "account.data_account_type_other_income",
    "account.data_account_type_payable",
    "account.data_account_type_prepayments",
    "account.data_account_type_receivable",
    "account.data_account_type_revenue",
    "account.data_unaffected_earnings",
    "account.account_tax_carryover_line_comp_rule",
    "account.analytic_default_comp_rule",
]


def _fill_account_bank_statement_attachment_ids(env):
    """The chatter attachments of the bank statements are now linked through
    the new `attachment_ids` many2many field, so we fill it with the existing ones.
    """
    openupgrade.logged_query(
        env.cr,
        """
        INSERT INTO account_bank_statement_ir_attachment_rel
            (account_bank_statement_id, ir_attachment_id)
        SELECT ia.res_id, ia.id
        FROM account_bank_statement abs
            JOIN ir_attachment ia ON abs.id = ia.res_id
        WHERE ia.res_model = 'account.bank.statement'
        """,
    )


def _compute_remaining_account_payment_amount_company_currency_signed(env):
    """Those payment with different currency than the company ones are not easily
    computed by SQL, so we use ORM for these cases, but they should luckily be few.
    """
    payments = env["account.payment"].search(
        [("amount_company_currency_signed", "=", False)]
    )
    payments._compute_amount_company_currency_signed()


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.load_data(env.cr, "account", "16.0.1.2/noupdate_changes.xml")
    openupgrade.delete_record_translations(env.cr, "account", _translations_to_delete)
    openupgrade.delete_records_safely_by_xml_id(
        env,
        _deleted_xml_records,
    )
    _fill_account_bank_statement_attachment_ids(env)
    _compute_remaining_account_payment_amount_company_currency_signed(env)
    # credit_limit converted to company dependent
    old_column = openupgrade.get_legacy_name("credit_limit")
    openupgrade.convert_to_company_dependent(
        env, "res.partner", old_column, "credit_limit"
    )
