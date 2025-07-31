""" Encode any known changes to the database here
to help the matching process
"""

# Renamed modules is a mapping from old module name to new module name
renamed_modules = {
    # odoo
    "note": "project_todo",
    "website_sale_delivery_mondialrelay": "website_sale_mondialrelay",
    # odoo/enterprise
    # OCA/delivery-carrier
    "delivery_carrier_customer_info": "partner_delivery_info",
    # OCA/social
    "mail_activity_unlink_log": "mail_activity_cancel_tracking",
}

# Merged modules contain a mapping from old module names to other,
# preexisting module names
merged_modules = {
    # odoo
    "account_payment_invoice_online_payment_patch": "account_payment",
    "account_sequence": "account",
    "association": "membership",
    "l10n_de_skr03": "l10n_de",
    "l10n_de_skr04": "l10n_de",
    "l10n_generic_coa": "account",
    "l10n_hr_euro": "l10n_hr",
    "l10n_in_tcs_tds": "l10n_in",
    "l10n_in_upi": "l10n_in",
    "l10n_latam_account_sequence": "l10n_latam_invoice_document",
    "l10n_multilang": "account",
    "loyalty_delivery": "sale_loyalty_delivery",
    "pos_cache": "point_of_sale",
    "pos_daily_sales_reports": "point_of_sale",
    "pos_epson_printer_restaurant": "point_of_sale",
    "purchase_price_diff": "purchase_stock",
    "spreadsheet_dashboard_sale_expense": "spreadsheet_dashboard_hr_expense",
    "web_kanban_gauge": "web",
    "website_event_crm_questions": "website_event_crm",
    "website_event_questions": "website_event",
    "website_sale_delivery": "website_sale",
    "website_sale_digital": "website_sale",
    "website_sale_loyalty_delivery": "website_sale_loyalty",
    "website_sale_stock_product_configurator": "website_sale_product_configurator",
    # OCA/account-invoicing
    "account_invoice_fiscal_position_update": "account",
    # OCA/e-commerce
    "website_sale_invoice_address": "website_sale",
    # OCA/hr-attendance
    "hr_attendance_geolocation": "hr_attendance",
    # OCA/l10n-germany
    "l10n_de_skr03_mis_reports": "l10n_de_mis_reports",
    "l10n_de_skr04_mis_reports": "l10n_de_mis_reports",
    # OCA/l10n-spain
    "l10n_es_dua": "l10n_es",
    "l10n_es_dua_sii": "l10n_es_aeat_sii_oca",
    "l10n_es_irnr": "l10n_es",
    "l10n_es_irnr_sii": "l10n_es_aeat_sii_oca",
    # OCA/maintenance
    "base_maintenance_config": "maintenance",
    "maintenance_plan": "maintenance",
    "maintenance_plan_activity": "maintenance",
    "maintenance_plan_employee": "maintenance",
    # OCA/product-attribute
    "product_catalog": "product",
    "product_catalog_sale": "sale",
    # OCA/purchase-workflow
    "purchase_discount": "purchase",
    # OCA/sale-promotion
    "loyalty_initial_date_validity": "loyalty",
    "sale_loyalty_initial_date_validity": "sale_loyalty",
    # OCA/sale-reporting
    "sale_report_country_state": "sale",
    # OCA/social
    "mail_activity_plan": "mail",
    "mass_mailing_custom_unsubscribe_event": "mass_mailing",
    # OCA/stock-logistics-warehouse
    "stock_lot_filter_available": "stock",
    # OCA/web
    "web_advanced_search": "web",
    "web_listview_range_select": "web",
    "web_pwa_oca": "web",
    # OCA/...
}

# only used here for upgrade_analysis
renamed_models = {
    # odoo
    "hr.leave.stress.day": "hr.leave.mandatory.day",
    "mail.channel": "discuss.channel",
    "mail.channel.member": "discuss.channel.member",
    "mail.channel.rtc.session": "discuss.channel.rtc.session",
    "mailing.contact.subscription": "mailing.subscription",
    "payment.icon": "payment.method",
    "restaurant.printer": "pos.printer",
    # OCA/...
}

# only used here for upgrade_analysis
merged_models = {
    # odoo
    "repair.line": "stock.move",
    # OCA/...
}
