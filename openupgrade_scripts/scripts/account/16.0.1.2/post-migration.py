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


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.load_data(env.cr, "account", "16.0.1.2/noupdate_changes.xml")
    openupgrade.delete_record_translations(env.cr, "account", _translations_to_delete)
    openupgrade.delete_records_safely_by_xml_id(
        env,
        _deleted_xml_records,
    )
