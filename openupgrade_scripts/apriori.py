""" Encode any known changes to the database here
to help the matching process
"""

# Renamed modules is a mapping from old module name to new module name
renamed_modules = {
    # odoo
    "note": "project_todo",
    "website_sale_delivery_mondialrelay": "website_sale_mondialrelay",
    # odoo/enterprise
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
    "loyalty_delivery": "sale_loyalty_delivery",
    "pos_cache": "point_of_sale",
    "pos_daily_sales_reports": "point_of_sale",
    "pos_epson_printer_restaurant": "point_of_sale",
    "purchase_price_diff": "purchase_stock",
    "web_kanban_gauge": "web",
    "website_event_crm_questions": "website_event_crm",
    "website_event_questions": "website_event",
    "website_sale_delivery": "website_sale",
    "website_sale_loyalty_delivery": "website_sale_loyalty",
    "website_sale_stock_product_configurator": "website_sale_product_configurator",
    # OCA/l10n-spain
    "l10n_es_irnr": "l10n_es",
    "l10n_es_irnr_sii": "l10n_es_aeat_sii_oca",
    # OCA/maintenance
    "base_maintenance_config": "maintenance",
    "maintenance_plan": "maintenance",
    "maintenance_plan_activity": "maintenance",
    # OCA/purchase-workflow
    "purchase_discount": "purchase",
    # OCA/social
    "mail_activity_plan": "mail",
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
