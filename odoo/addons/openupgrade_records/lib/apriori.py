""" Encode any known changes to the database here
to help the matching process
"""

renamed_modules = {
    # Odoo
    'crm_reveal': 'crm_iap_lead',
    'document': 'attachment_indexation',
    'payment_ogone': 'payment_ingenico',
    # OCA/delivery-carrier
    'delivery_carrier_label_ups': 'delivery_ups_oca',
    # OCA/edi
    'edi_oca': 'edi',
    # OCA/event
    'website_event_filter_selector': 'website_event_filter_city',
    # OCA/hr
    # TODO: Transform possible data
    'hr_skill': 'hr_skills',
    # OCA/iot
    'iot': 'iot_oca',
    'iot_amqp': 'iot_amqp_oca',
    'iot_input': 'iot_input_oca',
    'iot_output': 'iot_output_oca',
    # OCA/manufacture
    'quality_control': 'quality_control_oca',
    'quality_control_mrp': 'quality_control_mrp_oca',
    'quality_control_stock': 'quality_control_stock_oca',
    'quality_control_team': 'quality_control_team_oca',
    # OCA/margin-analysis
    'product_pricelist_margin': 'product_pricelist_simulation',
    # OCA/pos
    'pos_journal_image': 'pos_payment_method_image',
    # OCA/product-attribute
    'product_pricelist_print_website_sale': 'product_pricelist_direct_print_website_sale',
    'sale_product_classification': 'product_abc_classification_sale',
    # OCA/stock-logistics-warehouse
    'stock_putaway_product_form': 'stock_putaway_product_template',
    # OCA/l10n-netherlands -> OCA/account-financial-reporting
    'l10n_nl_mis_reports': 'mis_template_financial_report',
}

merged_modules = {
    # Odoo
    'account_cancel': 'account',
    'account_voucher': 'account',
    'crm_phone_validation': 'crm',
    'decimal_precision': 'base',
    'delivery_hs_code': 'delivery',
    'hw_scale': 'hw_drivers',
    'hw_scanner': 'hw_drivers',
    'hw_screen': 'hw_drivers',
    'l10n_fr_certification': 'account',
    'l10n_fr_sale_closing': 'l10n_fr',
    'mrp_bom_cost': 'mrp_account',
    'mrp_byproduct': 'mrp',
    'payment_stripe_sca': 'payment_stripe',
    'stock_zebra': 'stock',
    'survey_crm': 'survey',
    'test_pylint': 'test_lint',
    'web_settings_dashboard': 'base_setup',
    'website_crm_phone_validation': 'website_crm',
    'website_sale_link_tracker': 'website_sale',
    'website_survey': 'survey',
    # OCA/account-financial-tools
    'account_coa_menu': 'account_menu',
    'account_group_menu': 'account_menu',
    'account_move_chatter': 'account',
    'account_tag_menu': 'account_menu',
    'account_type_menu': 'account_menu',
    # OCA/account-invoicing
    'account_invoice_repair_link': 'repair',
    # OCA/account-reconcile
    'account_set_reconcilable': 'account',
    'bank_statement_foreign_currency': 'account',
    'account_reconciliation_widget_partial': 'account',
    # OCA/e-commerce
    'website_sale_category_description': 'website_sale',
    # OCA/event
    'event_activity': 'event',
    'website_event_share': 'website_event',
    # OCA/geospatial
    'base_geolocalize_openstreetmap': 'base_geolocalize',
    # OCA/l10n-spain
    'l10n_es_account_invoice_sequence': 'l10n_es',
    'l10n_es_aeat_mod303_extra_data': 'l10n_es_aeat_mod303',
    'l10n_es_aeat_sii': 'l10n_es_aeat_sii_oca',
    'l10n_es_aeat_sii_extra_data': 'l10n_es_aeat_sii_oca',
    'l10n_es_extra_data': 'l10n_es',
    'l10n_es_ticketbai_batuz_extra_data': 'l10n_es_ticketbai_batuz',
    'l10n_es_ticketbai_extra_data': 'l10n_es_ticketbai',
    'l10n_es_vat_book_extra_data': 'l10n_es_vat_book',
    # OCA/manufacture
    'repair_calendar_view': 'base_repair',
    # OCA/multi-company
    'stock_production_lot_multi_company': 'stock',
    # OCA/partner-contact
    'base_vat_sanitized': 'base_vat',
    'partner_group': 'partner_company_group',
    # OCA/payroll
    'hr_payroll': 'payroll',
    'hr_payroll_account': 'payroll_account',
    # OCA/product-attribute
    'product_pricelist_show_product_ref': 'product',
    'product_active_propagate': 'product',
    # OCA/product-variant
    'sale_order_variant_mgmt': 'sale_product_matrix',
    # OCA/purchase-reporting
    'purchase_report_extension': 'purchase',
    # OCA/sale-workflow
    'sale_disable_inventory_check': 'sale_stock',
    # OCA/server-backend
    'base_suspend_security': 'base',
    # OCA/social
    'mail_history': 'mail',
    'mass_mailing_unique': 'mass_mailing',
    # OCA/stock-logistics-reporting
    'stock_forecast_report': 'stock',
    'stock_picking_report_custom_description': 'stock',
    # OCA/stock-logistics-warehouse
    'sale_stock_info_popup': 'sale_stock',
    # OCA/stock-logistics-workflow
    'stock_picking_responsible': 'stock',
    # OCA/timesheet
    'sale_timesheet_existing_project': 'sale_timesheet',
    # OCA/web
    'web_export_view': 'web',
    'web_favicon': 'base',
    'web_tree_resize_column': 'web',
    'web_view_searchpanel': 'web',
    'web_widget_color': 'web',
    'web_widget_float_formula': 'web',
    'web_widget_many2many_tags_multi_selection': 'web',
    'web_widget_one2many_product_picker_sale_stock_available_info_popup': (
        'web_widget_one2many_product_picker_sale_stock'
    ),
    # OCA/website
    'website_adv_image_optimization': 'website',
    'website_canonical_url': 'website',
    'website_form_builder': 'website_form',
    'website_logo': 'website',
    'website_megamenu': 'website',
    'website_snippet_anchor': 'website',
    'website_anchor_smooth_scroll': 'website',
    # muk-it/muk_base - Agreed to move to OCA
    'muk_attachment_lobject': 'dms',
    'muk_security': 'dms',
    'muk_autovacuum': 'dms',
    'muk_utils': 'dms',
    # muk-it/muk_web - Agreed to move to OCA
    'muk_web_preview': 'mail_preview_base',
    'muk_web_preview_audio': 'mail_preview_audio',
    'muk_web_preview_image': 'mail_preview_base',
    'muk_web_preview_video': 'mail_preview_base',
    'muk_web_searchpanel': 'web',
    'muk_web_utils': 'dms',
    # muk-it/muk_dms - Agreed to move to OCA
    'muk_dms': 'dms',
    'muk_dms_access': 'dms',
    'muk_dms_actions': 'dms',
    'muk_dms_attachment': 'dms',
    'muk_dms_field': 'dms',
    'muk_dms_file': 'dms',
    'muk_dms_lobject': 'dms',
    'muk_dms_mail': 'dms',
    'muk_dms_thumbnails': 'dms',
    'muk_dms_view': 'dms',
}

# only used here for openupgrade_records analysis:
renamed_models = {
    # Odoo
    'account.register.payments': 'account.payment.register',
    'crm.reveal.industry': 'crm.iap.lead.industry',
    'crm.reveal.role': 'crm.iap.lead.role',
    'crm.reveal.seniority': 'crm.iap.lead.seniority',
    'mail.blacklist.mixin': 'mail.thread.blacklist',
    'mail.mail.statistics': 'mailing.trace',
    'mail.statistics.report': 'mailing.trace.report',
    'mail.mass_mailing': 'mailing.mailing',
    'mail.mass_mailing.contact': 'mailing.contact',
    'mail.mass_mailing.list': 'mailing.list',
    'mail.mass_mailing.list_contact_rel': 'mailing.contact.subscription',
    'mail.mass_mailing.stage': 'utm.stage',
    'mail.mass_mailing.tag': 'utm.tag',
    'mail.mass_mailing.test': 'mailing.mailing.test',
    'mass.mailing.list.merge': 'mailing.list.merge',
    'mass.mailing.schedule.date': 'mailing.mailing.schedule.date',
    'mrp.subproduct': 'mrp.bom.byproduct',
    'sms.send_sms': 'sms.composer',
    'stock.fixed.putaway.strat': 'stock.putaway.rule',
    'report.stock.forecast': 'report.stock.quantity',
    'survey.mail.compose.message': 'survey.invite',
    'website.redirect': 'website.rewrite',
    # OCA/...
}

# only used here for openupgrade_records analysis:
merged_models = {
    # Odoo
    'account.invoice': 'account.move',
    'account.invoice.line': 'account.move.line',
    'account.invoice.tax': 'account.move.line',
    'account.voucher': 'account.move',
    'account.voucher.line': 'account.move.line',
    'lunch.order.line': 'lunch.order',
    'mail.mass_mailing.campaign': 'utm.campaign',
    'slide.category': 'slide.slide',
    'survey.page': 'survey.question',
    # OCA/...
}
