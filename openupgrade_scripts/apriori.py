""" Encode any known changes to the database here
to help the matching process
"""

# Renamed modules is a mapping from old module name to new module name
renamed_modules = {
    # odoo
    "crm_iap_lead": "crm_iap_mine",
    "crm_iap_lead_enrich": "crm_iap_enrich",
    "crm_iap_lead_website": "website_crm_iap_reveal",
    "mail_client_extension": "mail_plugin",
    "payment_ingenico": "payment_ogone",
    "website_mail_channel": "website_mail_group",
    # OCA/account-fiscal-rule
    "l10n_eu_oss": "l10n_eu_oss_oca",
    # OCA/e-commerce
    "website_sale_attribute_filter_order": "website_sale_product_attribute_filter_order",
    # OCA/project
    "project_stage_state": "project_task_stage_state",
    # OCA/sale-promotion
    "sale_coupon_chatter": "coupon_chatter",
    "sale_coupon_commercial_partner_applicability": "coupon_commercial_partner_applicability",
    "sale_coupon_mass_mailing": "coupon_mass_mailing",
    "sale_coupon_portal": "coupon_portal",
    "sale_coupon_portal_commercial_partner_applicability": "coupon_portal_commercial_partner_applicability",  # noqa: B950
    # OCA/stock-logistics-worehouse
    "stock_inventory_cost_info": "stock_quant_cost_info",
    # OCA/...
}

# Merged modules contain a mapping from old module names to other,
# preexisting module names
merged_modules = {
    # odoo
    "account_edi_extended": "account_edi",
    "l10n_be_invoice_bba": "l10n_be",
    "l10n_eu_service": "l10n_eu_oss",  # due to OCA/account-fiscal-rule
    "l10n_ch_qr_iban": "l10n_ch",
    "l10n_se_ocr": "l10n_se",
    "payment_adyen_paybylink": "payment_adyen",
    "payment_fix_register_token": "payment",
    "procurement_jit": "sale_stock",
    "sale_timesheet_edit": "sale_timesheet",
    "sale_timesheet_purchase": "sale_timesheet",
    "website_event_track_exhibitor": "website_event_exhibitor",
    "website_form": "website",
    "website_sale_management": "website_sale",
    # odoo/design-themes
    "website_animate": "website",
    # odoo/enterprise
    "stock_barcode_mobile": "stock_barcode",
    # OCA/account-financial-tools
    "stock_account_prepare_anglo_saxon_out_lines_hook": "stock_account",
    # OCA/e-commerce
    "website_sale_product_attribute_filter_visibility": "website_sale",
    "account_menu": "account_usability",
    # OCA/account-invoicing
    "purchase_invoicing_no_zero_line": "purchase",
    # OCA/account-invoicing
    "purchase_batch_invoicing": "purchase",
    # OCA/e-commerce
    "website_sale_cart_no_redirect": "website_sale",
    # OCA/hr
    "hr_recruitment_notification": "hr_recruitment",
    # OCA/e-commerce
    "website_sale_attribute_filter_price": "website_sale",
    "website_sale_stock_available_display": "website_sale_stock",
    # OCA/hr-attendance
    "hr_attendance_user_list": "hr_attendance",
    # OCA/product-attribute
    "stock_account_product_cost_security": "product_cost_security",
    # OCA/stock-logistics-reporting
    "stock_inventory_valuation_pivot": "stock_account",
    # OCA/stock-logistics-warehouse
    "stock_inventory_exclude_sublocation": "stock",
    "stock_orderpoint_manual_procurement": "stock",
    # OCA/stock-logistics-workflow
    "stock_deferred_assign": "stock",
    "stock_move_assign_picking_hook": "stock",
    # OCA/survey
    "survey_description": "survey",
    # OCA/project
    "project_mail_chatter": "project",
    "project_task_dependency": "project",
    "project_timeline_task_dependency": "project_timeline",
    # OCA/timesheet
    "sale_timesheet_order_line_sync": "sale_timesheet",
    # OCA/web
    "web_decimal_numpad_dot": "web",
    # OCA/website
    "website_google_analytics_4": "website",
    "website_snippet_timeline": "website",
}

# only used here for upgrade_analysis
renamed_models = {
    # odoo
    "calendar.contacts": "calendar.filters",
    "mail.moderation": "mail.group.moderation",
    # OCA/...
}

# only used here for upgrade_analysis
merged_models = {
    "stock.inventory": "stock.quant",
    "stock.inventory.line": "stock.move.line",
}
