"""Encode any known changes to the database here
to help the matching process
"""

# Renamed modules is a mapping from old module name to new module name
renamed_modules = {
    # odoo
    "l10n_ec_website_sale": "l10n_ec_sale",
    "l10n_in_edi_ewaybill": "l10n_in_ewaybill",
    "pos_viva_wallet": "pos_viva_com",
    # odoo/enterprise
    # OCA/timesheet
    "project_timesheet_time_control": "hr_timesheet_time_control",
    # OCA/...
}

# Merged modules contain a mapping from old module names to other,
# preexisting module names
merged_modules = {
    # odoo
    "account_edi_ubl_cii_tax_extension": "account_edi_ubl_cii",
    "account_peppol_selfbilling": "account_peppol",
    "auth_totp_mail_enforce": "auth_totp_mail",
    "hr_contract": "hr",
    "hr_holidays_contract": "hr_holidays",
    "hr_work_entry_contract": "hr_work_entry",
    "l10n_es_modelo130": "l10n_es",
    "l10n_id_efaktur": "l10n_id_efaktur_coretax",
    "l10n_in_gstin_status": "l10n_in",
    "l10n_in_withholding": "l10n_in",
    "l10n_in_withholding_payment": "l10n_in",
    "l10n_it_edi_ndd": "l10n_it_edi",
    "l10n_it_edi_ndd_account_dn": "l10n_it_edi",
    "l10n_it_edi_website_sale": "l10n_it_edi",
    "l10n_it_edi_withholding": "l10n_it_edi",
    "l10n_jo_edi_extended": "l10n_jo_edi",
    "l10n_my_edi_extended": "l10n_my_edi",
    "l10n_pe_website_sale": "l10n_pe",
    "l10n_pl_taxable_supply_date": "l10n_pl",
    "l10n_ro_efactura_synchronize": "l10n_ro_edi",
    "payment_razorpay_oauth": "payment_razorpay",
    "pos_epson_printer": "point_of_sale",
    "pos_self_order_epson_printer": "pos_self_order",
    "sale_async_emails": "sale",
    "web_editor": "html_editor",
    # odoo/enterprise
    # OCA/account-invoicing
    "account_tax_legal_notes_translate": "account",
    # OCA/account-reconcile
    "account_reconcile_model_oca": "account_reconcile_oca",
    # OCA/bank-payment
    "account_payment_partner": "account_payment_mode",
    # OCA/partner-contact
    "partner_contact_lang": "base",
    # OCA/project
    "project_task_add_very_high": "project",
    # OCA/purchase-workflow
    "purchase_order_qty_change_no_recompute": "purchase",
    # OCA/sale-workflow
    "sale_order_warn_message": "sale",
    # OCA/stock-logistics-workflow
    "stock_picking_show_return": "stock",
    # OCA/vertical-association
    "membership_extension": "membership",
}

# only used here for upgrade_analysis
renamed_models = {
    # odoo
    "account_peppol.service.wizard": "peppol.config.wizard",
    "hr.attendance.overtime": "hr.attendance.overtime.line",
    "hr.candidate.skill": "hr.applicant.skill",
    "hr.contract": "hr.version",
    "mail.wizard.invite": "mail.followers.edit",
    "mrp.batch.produce": "mrp.production.serials",
    "procurement.group": "stock.reference",
    "product.packaging": "product.uom",
    "stock.package_level": "stock.package.history",
    "stock.quant.package": "stock.package",
    "stock.valuation.layer": "product.value",
    "web_editor.assets": "website.assets",
    "web_editor.converter.test": "html_editor.converter.test",
    "web_editor.converter.test.sub": "html_editor.converter.test.sub",
    # OCA/...
}

# only used here for upgrade_analysis
merged_models = {
    # odoo
    "hr.candidate": "hr.applicant",
    # OCA/...
}
