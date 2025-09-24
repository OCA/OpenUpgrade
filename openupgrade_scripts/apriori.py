""" Encode any known changes to the database here
to help the matching process
"""

# Renamed modules is a mapping from old module name to new module name
renamed_modules = {
    # odoo
    "l10n_es_pos_tbai": "l10n_es_edi_tbai_pos",
    "mrp_subonctracting_landed_costs": "mrp_subcontracting_landed_costs",
    "spreadsheet_dashboard_purchase": "spreadsheet_dashboard_purchase_oca",
    "spreadsheet_dashboard_purchase_stock": "spreadsheet_dashboard_purchase_stock_oca",
    "website_sale_picking": "website_sale_collect",
    "website_form_project": "website_project",
    # odoo/enterprise
    # OCA/commission
    "account_commission": "account_commission_oca",
    "commission": "commission_oca",
    "hr_commission": "hr_commission_oca",
    "sale_commission": "sale_commission_oca",
    # OCA/edi
    "pdf_helper": "pdf_xml_attachment",
    # OCA/product-attribute
    "product_packaging_type_vendor": "product_packaging_level_vendor",
    "product_supplierinfo_for_customer": "product_customerinfo",
    "product_supplierinfo_import_by_barcode": "product_supplierinfo_import",
    "product_supplierinfo_import_by_barcode_margin": "product_supplierinfo_import_margin",  # noqa: E501
    "product_template_tags_code": "product_tags_code",
    "stock_packaging_calculator": "product_packaging_calculator",
    # OCA/project
    "project_stock": "project_task_stock",
    "project_stock_product_set": "project_task_stock_product_set",
    # OCA/sale-promotion
    "coupon_chatter": "loyalty_program_chatter",
    # OCA/sale-workflow
    "product_supplierinfo_for_customer_sale": "product_customerinfo_sale",
    "product_supplierinfo_for_customer_elaboration": "product_customerinfo_elaboration",
    "sale_product_set_sale_by_packaging": "product_set_sell_only_by_packaging",
    # OCA/stock-logistics-workflow
    "stock_picking_type_shipping_policy": "stock_picking_type_force_move_type",
    # OCA/web
    "web_widget_product_label_section_and_note": "web_widget_product_label_section_and_note_name_visibility",  # noqa: E501
    # OCA/...
}

# Merged modules contain a mapping from old module names to other,
# preexisting module names
merged_modules = {
    # odoo
    "account_audit_trail": "account",
    "account_lock": "account",
    "account_payment_term": "account",
    "l10n_br_pix": "l10n_br",
    "l10n_de_audit_trail": "l10n_de",
    "l10n_dk_audit_trail": "l10n_dk",
    "l10n_dk_bookkeeping": "account",
    "l10n_es_edi_facturae_adm_centers": "l10n_es_edi_facturae",
    "l10n_es_edi_facturae_invoice_period": "l10n_es_edi_facturae",
    "l10n_es_edi_tbai_multi_refund": "l10n_es_edi_tbai",
    "l10n_fr_fec": "l10n_fr_account",
    "l10n_fr_invoice_addr": "l10n_fr_account",
    "l10n_ro_efactura": "l10n_ro_edi",
    "im_livechat_mail_bot": "mail_bot",
    "payment_ogone": "payment_worldline",
    "payment_sips": "payment_worldline",
    "pos_sale_product_configurator": "pos_sale",
    "sale_product_configurator": "sale",
    "stock_landed_costs_company": "stock_landed_costs",
    "website_sale_product_configurator": "website_sale",
    # odoo/enterprise
    # OCA/account-invoicing
    "account_invoice_mass_sending": "account",
    "account_invoice_supplierinfo_update_discount": "account_invoice_supplierinfo_update",  # noqa: E501
    # OCA/e-commerce
    "website_sale_product_attachment": "website_sale",
    "website_sale_product_attribute_filter_collapse": "website_sale",
    # OCA/hr-attendance
    "hr_attendance_autoclose": "hr_attendance",
    # OCA/knowledge
    "document_page_group": "document_page_access_group",
    # OCA/l10n-france
    "l10n_fr_pos_cert_update_draft_order_line": "l10n_fr_pos_cert",
    # OCA/sale-workflow
    "sale_order_qty_change_no_recompute": "sale",
    # OCA/server-brand
    "hr_expense_remove_mobile_link": "hr_expense",
    # OCA/...
}

# only used here for upgrade_analysis
renamed_models = {
    # odoo
    "hr.applicant.skill": "hr.candidate.skill",
    "l10n_es_edi_facturae_adm_centers.ac_role_type": ""
    "l10n_es_edi_facturae.ac_role_type",
    "mail.notification.web.push": "mail.push",
    "mail.partner.device": "mail.push.device",
    "mail.shortcode": "mail.canned.response",
    "pos.combo": "product.combo",
    "pos.combo.line": "product.combo.item",
    # OCA/...
}

# only used here for upgrade_analysis
merged_models = {
    # odoo
    "google.calendar.credentials": "res.users.settings",
    "l10n_es_edi.certificate": "certificate.certificate",
    "l10n_es_edi_facturae.certificate": "certificate.certificate",
    "l10n_es_edi_verifactu.certificate": "certificate.certificate",
    "microsoft.calendar.credentials": "res.users.settings",
    "mrp.document": "product.document",
    # OCA/...
}
