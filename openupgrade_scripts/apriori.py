""" Encode any known changes to the database here
to help the matching process
"""

# Renamed modules is a mapping from old module name to new module name
renamed_modules = {
    # odoo
    "account_facturx": "account_edi_facturx",
    "sale_coupon": "coupon",
    "website_rating": "portal_rating",
    # OCA/account-invoice-reporting
    "account_invoice_comment_template": "account_comment_template",
    # OCA/bank-statement-import
    "account_bank_statement_import": "account_statement_import",  # from odoo
    "account_bank_statement_import_bypass_check": "account_statement_import_bypass_check",  # noqa: B950
    "account_bank_statement_clear_partner": "account_statement_clear_partner",
    "account_bank_statement_import_camt_details": "account_statement_import_camt_details",  # noqa: B950
    "account_bank_statement_import_camt_oca": "account_statement_import_camt_oca",
    "account_bank_statement_import_move_line": "account_statement_import_move_line",
    "account_bank_statement_import_mt940_base": "account_statement_import_mt940_base",
    "account_bank_statement_import_oca_camt54": "account_statement_import_oca_camt54",
    "account_bank_statement_import_ofx": "account_statement_import_ofx",
    "account_bank_statement_import_online": "account_statement_import_online",
    "account_bank_statement_import_online_paypal": "account_statement_import_online_paypal",  # noqa: B950
    "account_bank_statement_import_online_ponto": "account_statement_import_online_ponto",  # noqa: B950
    "account_bank_statement_import_online_transferwise": "account_statement_import_online_transferwise",  # noqa: B950
    "account_bank_statement_import_paypal": "account_statement_import_paypal",
    "account_bank_statement_import_qif": "account_statement_import_qif",
    "account_bank_statement_import_split": "account_statement_import_split",
    "account_bank_statement_import_save_file": "account_statement_import_save_file",
    "account_bank_statement_import_transfer_move": "account_statement_import_transfer_move",  # noqa: B950
    "account_bank_statement_import_txt_xlsx": "account_statement_import_txt_xlsx",
    # OCA/edi
    "account_e-invoice_generate": "account_einvoice_generate",
    "edi": "edi_oca",
    "edi_account": "edi_account_oca",
    "edi_backend_partner": "edi_backend_partner_oca",
    "edi_exchange_template": "edi_exchange_template_oca",
    "edi_storage": "edi_storage_oca",
    "edi_voxel": "edi_voxel_oca",
    "edi_webservice": "edi_webservice_oca",
    "edi_xml": "edi_xml_oca",
    # OCA/l10n-spain
    "l10n_es_account_bank_statement_import_n43": "l10n_es_account_statement_import_n43",
    # OCA/server-tools
    "openupgrade_records": "upgrade_analysis",
    # OCA/web
    "web_confirm_duplicate": "web_copy_confirm",
    # OCA/...
}

# Merged modules contain a mapping from old module names to other,
# preexisting module names
merged_modules = {
    # odoo
    "account_analytic_default": "account",
    "account_analytic_default_hr_expense": "hr_expense",
    "account_analytic_default_purchase": "purchase",
    "hr_expense_check": "hr_expense",
    "hr_holidays_calendar": "hr_holidays",
    "hw_proxy": "hw_drivers",
    "l10n_cn_small_business": "l10n_cn",
    "partner_autocomplete_address_extended": "base_address_extended",
    "payment_stripe_checkout_webhook": "payment_stripe",
    "pos_cash_rounding": "point_of_sale",
    "pos_kitchen_printer": "pos_restaurant",
    "pos_reprint": "point_of_sale",
    "theme_default": "website",
    "website_theme_install": "website",
    # odoo/design-themes
    "theme_graphene_blog": "theme_graphene",
    # odoo/enterprise
    "hr_holidays_gantt_calendar": "hr_holidays_gantt",
    # OCA/intrastat-extrastat
    "hs_code_link": "product_harmonized_system_delivery",
    # OCA/event
    "website_event_questions_free_text": "website_event_questions",
    # OCA/margin-analysis
    "sale_order_margin_percent": "sale_margin",
    # OCA/partner-contact
    "base_vat_sanitized": "base_vat",
    "partner_bank_active": "base",
    # OCA/project
    "project_description": "project",
    "project_stage_closed": "project",
    # OCA/reporting-engine
    "bi_sql_editor_aggregate": "bi_sql_editor",
    # OCA/sale-reporting
    "report_qweb_pdf_fixed_column": "web",
    # OCA/sale-workflow
    "sale_order_price_recalculation": "sale",
    # OCA/stock-logistics-warehouse
    "stock_inventory_include_exhausted": "stock",
    # OCA/web
    "web_editor_background_color": "web_editor",
    # OCA/website
    "website_cookie_notice": "website",
    # OCA/...
}

# only used here for upgrade_analysis
renamed_models = {
    # odoo
    "crm.lead.tag": "crm.tag",
    "email_template.preview": "mail.template.preview",
    "event.answer": "event.question.answer",
    "product.style": "product.ribbon",
    "report.sale_coupon.report_coupon": "report.coupon.report_coupon",
    "sale.coupon": "coupon.coupon",
    "sale.coupon.generate": "coupon.generate.wizard",
    "sale.coupon.program": "coupon.program",
    "sale.coupon.reward": "coupon.reward",
    "sale.coupon.rule": "coupon.rule",
    "survey.user_input_line": "survey.user_input.line",
    "survey.label": "survey.question.answer",
    # OCA/bank-statement-import
    "account.bank.statement.import": "account.statement.import",
    # OCA/server-tools
    "openupgrade.analysis.wizard": "upgrade.analysis",
    "openupgrade.attribute": "upgrade.attribute",
    "openupgrade.comparison.config": "upgrade.comparison.config",
    "openupgrade.record": "upgrade.record",
    "openupgrade.generate.records.wizard": "upgrade.generate.record.wizard",
    "openupgrade.install.all.wizard": "upgrade.install.wizard",
}

# only used here for upgrade_analysis
merged_models = {}
