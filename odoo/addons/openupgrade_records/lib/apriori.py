""" Encode any known changes to the database here
to help the matching process
"""

renamed_modules = {
    # OCA/account-invoice-reporting
    'account_invoice_group_picking':
    'account_invoice_report_grouped_by_picking',
    # OCA/connector
    # Connector module has been unfolded in 2 modules in version 10.0:
    # connector and queue_job. We need to do this to correct upgrade both
    # modules.
    'connector': 'queue_job',
    # OCA/connector-magento
    'magentoerpconnect': 'connector_magento',
    # OCA/e-commerce
    'website_sale_qty': 'website_sale_price_tier',
    # OCA/hr
    # The OCA extensions of the hr_holidays module are 'hr_holidays_something'
    'hr_holiday_notify_employee_manager':
        'hr_holidays_notify_employee_manager',
    # OCA/hr-timesheet
    'hr_timesheet_sheet_restrict_analytic':
        'hr_timesheet_sheet_restrict_project',
    # OCA/manufacture-reporting:
    'report_mrp_bom_matrix': 'mrp_bom_matrix_report',
    # OCA/partner-contact:
    'res_partner_affiliate': 'partner_affiliate',
    # OCA/project
    'project_task_materials': 'project_task_material',
    # OCA/sale-workflow:
    'sale_delivery_block': 'sale_stock_picking_blocking',
    'sale_delivery_block_proc_group_by_line':
        'sale_stock_picking_blocking_proc_group_by_line',
    # OCA/server-tools:
    'mail_log_messages_to_process': 'mail_log_message_to_process',
    # OCA/stock-logistics-workflow:
    'product_customer_code_picking':
        'product_supplierinfo_for_customer_picking',
}

merged_modules = [
    ('account_full_reconcile', 'account'),
    ('mail_tip', 'mail'),
    ('mrp_operations', 'mrp'),
    ('project_timesheet', 'hr_timesheet'),
    ('sale_service', 'sale_timesheet'),
    ('share', 'base'),
    ('web_tip', 'web'),
    ('web_view_editor', 'web'),
    ('mail_tip', 'mail'),
    ('im_odoo_support', 'im_livechat'),
    ('marketing', 'marketing_campaign'),
    ('website_sale_stock_control', 'website_sale_stock'),
    ('test_pylint', 'test_lint'),
    # OCA/account-invoicing
    ('purchase_stock_picking_return_invoicing_open_qty',
     'purchase_stock_picking_return_invoicing'),
    ('sale_stock_picking_return_invoicing', 'sale_stock'),
    # OCA/account-financial-reporting
    ('account_journal_report', 'account_financial_report_qweb'),
    # OCA/e-commerce
    ('website_sale_b2c', 'sale'),  # used groups are in sale
    # OCA/manufacture
    ('mrp_production_unreserve', 'mrp'),
    # OCA/purchase-workflow
    ('purchase_fiscal_position_update', 'purchase'),
    # OCA/sale-workflow
    ('sale_order_back2draft', 'sale'),
    ('product_customer_code_sale',
     'product_supplierinfo_for_customer_sale'),
    # OCA/social
    ('mass_mailing_security_group', 'mass_mailing'),
    # OCA/stock-logistics-workflow
    ('stock_scrap', 'stock'),
    # OCA/web
    ('web_easy_switch_company', 'web'),
    # OCA/website
    ('website_blog_mgmt', 'website_blog'),
    ('website_blog_share', 'website_blog'),
    ('website_img_bg_style', 'website'),
    # OCA/l10n-brazil
    ('l10n_br_data_base', 'l10n_br_base'),
    ('l10n_br_data_account', 'l10n_br_account'),
    ('l10n_br_data_account_product', 'l10n_br_account_product'),
    ('l10n_br_data_account_service', 'l10n_br_account_service'),
]

renamed_models = {
}
