""" Encode any known changes to the database here
to help the matching process
"""

# Renamed modules is a mapping from old module name to new module name
renamed_modules = {
    # odoo
    "coupon": "loyalty",
    "payment_test": "payment_demo",
    "payment_transfer": "payment_custom",
    "pos_sale_gift_card": "pos_sale_loyalty",
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
    # "knowledge": "document_knowledge",
    # OCA/multi-company
    "res_partner_category_multi_company": "partner_category_multi_company",
    # OCA/project
    "project_stage_mgmt": "project_task_stage_mgmt",
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
    # SE7
    "se7_account_journal_fields_traking": "se7_account_journal_fields_tracking",
    "se7_project_form_partner": "se7_project_view_form_simplified_partner",
    "se7_project_kanban_to_form": "se7_project_kanban_open_form",
    "se7_project_task_scheduling": "se7_project_schedule",
    "se7_sale_mrp_line_associated_bom": "se7_sale_line_associated_bom",
    "se7_import_nominas_a3": "se7_import_account_move_payroll_a3",
    "se7_pg_export_a3": "se7_account_move_export_a3",
    "se7_account_invoice_tag": "se7_account_move_tag",
    # "se7_pg_yacht": "se7_boat_area", TODO: Pendent, lo millor seria fer se7_pg_yacht_area a s'Odoo 12.0
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
    "project_account": "project",
    "purchase_requisition_stock_dropshipping": "purchase_requisition_stock",
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
    # OCA/l10n-spain
    "l10n_es_irnr": "l10n_es",
    "l10n_es_irnr_sii": "l10n_es_aeat_sii_oca",
    # OCA/partner-contact
    "partner_company_group": "base_partner_company_group",
    # OCA/pos
    "pos_margin_account_invoice_margin": "point_of_sale",
    "pos_order_line_no_unlink": "point_of_sale",
    "pos_product_sort": "point_of_sale",
    # OCA/product-variant
    "purchase_variant_configurator_on_confirm": "purchase_variant_configurator",
    # OCA/project
    "project_task_milestone": "project",
    # OCA/purchase-workflow
    "product_form_purchase_link": "purchase",
    "purchase_order_line_price_history": "purchase",
    "purchase_picking_state": "purchase_stock",
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
    "web_tree_image_tooltip": "web",
    # SE7
    "se7_fc_sale_project_name": "se7_project_usability",
    "se7_hr_timesheet_filters": "se7_hr_timesheet_usability",
    "se7_fc_account": "se7_fusteriacomas",
    "se7_fc_account_invoice_report": "se7_fusteriacomas",
    "se7_fc_font": "se7_fusteriacomas",
    "se7_fc_hr_timesheet": "se7_fusteriacomas",
    "se7_fc_mrp": "se7_fusteriacomas",
    "se7_fc_project": "se7_fusteriacomas",
    "se7_fc_purchase": "se7_fusteriacomas",
    "se7_fc_sale": "se7_fusteriacomas",
    "se7_dni_company_contact": "se7_h2o2",
    "se7_h2o2_pago_pagare": "se7_h2o2",
    "se7_h2o2_sale": "se7_h2o2",
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

    # SE7
    # se7_account_invoice_tag / se7_account_move_tag
    "account.invoice.tag": "account.move.tag",
    # se7_pg_yacht / se7_boat_area TODO: Pendent, lo millor seria fer se7_pg_yacht_area a s'Odoo 12.0
    # "yacht.yacht": "boat.boat",
    # "yacht.area": "boat.area",
}

# only used here for upgrade_analysis
merged_models = {
    # odoo
    "gift.card": "loyalty.card",
    # OCA/...
}
