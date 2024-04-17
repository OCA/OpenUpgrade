""" Encode any known changes to the database here
to help the matching process
"""

# Renamed modules is a mapping from old module name to new module name
renamed_modules = {
    # odoo
    "coupon": "loyalty",
    "payment_test": "payment_demo",
    "payment_transfer": "payment_custom",
    "sale_coupon": "sale_loyalty",
    "sale_coupon_delivery": "sale_loyalty_delivery",
    "website_sale_coupon": "website_sale_loyalty",
    "website_sale_coupon_delivery": "website_sale_loyalty_delivery",
    # odoo/enterprise
    "helpdesk_sale_coupon": "helpdesk_sale_loyalty",
    "sale_coupon_taxcloud": "sale_loyalty_taxcloud",
    "sale_coupon_taxcloud_delivery": "sale_loyalty_taxcloud_delivery",
    # OCA/account-reconcile
    "account_reconciliation_widget": "account_reconcile_oca",
    # OCA/bank-statement-import
    "account_bank_statement_import_qif": "account_statement_import_qif",
    "account_statement_import": "account_statement_import_file",
    "account_statement_import_file_reconciliation_widget": (
        "account_statement_import_file_reconcile_oca"
    ),
    "account_statement_import_txt_xlsx": "account_statement_import_sheet_file",
    # OCA/crm
    "crm_project": "crm_lead_to_task",
    # OCA/knowledge
    "knowledge": "document_knowledge",
    # OCA/sale-promotion
    "coupon_incompatibility": "loyalty_incompatibility",
    "coupon_limit": "loyalty_limit",
    "coupon_mass_mailing": "loyalty_mass_mailing",
    "coupon_multi_gift": "loyalty_multi_gift",
    "coupon_criteria_multi_product": "loyalty_criteria_multi_product",
    "sale_coupon_criteria_multi_product": "sale_loyalty_criteria_multi_product",
    "sale_coupon_incompatibility": "sale_loyalty_incompatibility",
    "sale_coupon_limit": "sale_loyalty_limit",
    "sale_coupon_multi_gift": "sale_loyalty_multi_gift",
    "sale_coupon_order_line_link": "sale_loyalty_order_line_link",
    "sale_coupon_order_suggestion": "sale_loyalty_order_suggestion",
    "sale_coupon_partner": "sale_loyalty_partner",
    "website_sale_coupon_page": "website_sale_loyalty_page",
    "website_sale_coupon_selection_wizard": "website_sale_loyalty_suggestion_wizard",
    # OCA/server-ux
    "mass_editing": "server_action_mass_edit",
    # OCA/l10n-italy
    "l10n_it_ricevute_bancarie": "l10n_it_riba",
    # OCA/...
}

# Merged modules contain a mapping from old module names to other,
# preexisting module names
merged_modules = {
    # odoo
    "account_edi_facturx": "account_edi_ubl_cii",
    "account_edi_ubl": "account_edi_ubl_cii",
    "account_edi_ubl_bis3": "account_edi_ubl_cii",
    "account_sale_timesheet": "sale_project",
    "base_address_city": "base_address_extended",
    "fetchmail": "mail",
    "fetchmail_gmail": "google_gmail",
    "fetchmail_outlook": "microsoft_outlook",
    "gift_card ": "loyalty",
    "l10n_be_edi": "account_edi_ubl_cii",
    "l10n_nl_edi": "account_edi_ubl_cii",
    "l10n_no_edi": "account_edi_ubl_cii",
    "note_pad": "note",
    "pad": "web_editor",
    "pad_project": "project",
    "pos_coupon": "pos_loyalty",
    "pos_gift_card": "pos_loyalty",
    "sale_gift_card": "sale_loyalty",
    "sale_project_account": "sale_project",
    "website_sale_delivery_giftcard": "website_sale_loyalty_delivery",
    "website_sale_gift_card": "website_sale_loyalty",
    # OCA/account-financial-tools
    "account_balance_line": "account",
    "account_move_force_removal": "account",
    # OCA/account-invoicing
    "account_invoice_search_by_reference": "account",
    # OCA/account-invoice-reporting
    "account_invoice_report_due_list": "account",
    # OCA/e-commerce
    "website_sale_require_login": "website_sale",
    # OCA/pos
    "pos_order_line_no_unlink": "point_of_sale",
    "pos_product_sort": "point_of_sale",
    # OCA/project
    "project_task_milestone": "project",
    # OCA/purchase-workflow
    "product_form_purchase_link": "purchase",
    # OCA/sale-promotion
    "coupon_commercial_partner_applicability": "loyalty_partner_applicability",
    "sale_coupon_selection_wizard": "sale_loyalty_order_suggestion",
    # OCA/sale-workflow
    "sale_product_set_layout": "sale_product_set",
    # OCA/social
    "mail_preview_audio": "mail",
    "mail_preview_base": "mail",
    # OCA/stock-logistics-workflow
    "stock_picking_backorder_strategy": "stock",
    # OCA/web
    "web_drop_target": "web",
    "web_ir_actions_act_view_reload": "web",
}

# only used here for upgrade_analysis
renamed_models = {
    # odoo
    "account.analytic.group": "account.analytic.plan",
    "account.tax.carryover.line": "account.report.external.value",
    "account.tax.report": "account.report",
    "account.tax.report.line": "account.report.line",
    "coupon.coupon": "loyalty.card",
    "coupon.program": "loyalty.program",
    "coupon.reward": "loyalty.reward",
    "coupon.rule": "loyalty.rule",
    "mail.channel.partner": "mail.channel.member",
    "payment.acquirer": "payment.provider",
    "payment.acquirer.onboarding.wizard ": "payment.provider.onboarding.wizard",
    "sale.coupon.apply.code": "sale.loyalty.coupon.wizard",
    "sale.payment.acquirer.onboarding.wizard": "sale.payment.provider.onboarding.wizard",
    "stock.location.route": "stock.route",
    "stock.production.lot": "stock.lot",
    # OCA/...
}

# only used here for upgrade_analysis
merged_models = {
    # odoo
    "gift.card": "loyalty.card",
    # OCA/...
}
