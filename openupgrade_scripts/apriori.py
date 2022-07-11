""" Encode any known changes to the database here
to help the matching process
"""

# Renamed modules is a mapping from old module name to new module name
renamed_modules = {
    # odoo
    "crm_iap_lead": "crm_iap_mine",
    "crm_iap_lead_enrich": "crm_iap_enrich",
    "l10n_eu_service": "l10n_eu_oss",
    "mail_client_extension": "mail_plugin",
    "payment_ingenico": "payment_ogone",
    # OCA/project
    "project_stage_state": "project_task_stage_state",
    # OCA/...
}

# Merged modules contain a mapping from old module names to other,
# preexisting module names
merged_modules = {
    # odoo
    "account_edi_extended": "account_edi",
    "l10n_be_invoice_bba": "l10n_be",
    "l10n_ch_qr_iban": "l10n_ch",
    "l10n_se_ocr": "l10n_se",
    "payment_fix_register_token": "payment",
    "procurement_jit": "sale_stock",
    "sale_timesheet_edit": "sale_timesheet",
    "website_event_track_exhibitor": "website_event_exhibitor",
    "website_form": "website",
    "website_sale_management": "website_sale",
    # OCA/account-financial-tools
    "stock_account_prepare_anglo_saxon_out_lines_hook": "stock_account",
    # OCA/stock-logistics-workflow
    "stock_move_assign_picking_hook": "stock",
    # OCA/web
    "web_decimal_numpad_dot": "web",
}

# only used here for upgrade_analysis
renamed_models = {
    # odoo
    # OCA/...
}

# only used here for upgrade_analysis
merged_models = {}
