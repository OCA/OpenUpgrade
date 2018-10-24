""" Encode any known changes to the database here
to help the matching process
"""

renamed_modules = {
    # OCA/connector
    # Connector module has been unfolded in 2 modules in version 10.0:
    # connector and queue_job. We need to do this to correct upgrade both
    # modules.
    'connector': 'queue_job',
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
    # OCA/sale-workflow:
    'sale_delivery_block': 'sale_stock_picking_blocking',
    'product_customer_code_sale': 'product_supplierinfo_for_customer_sale',
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
    # OCA/account-invoicing
    ('purchase_stock_picking_return_invoicing_open_qty',
     'purchase_stock_picking_return_invoicing'),
    ('sale_stock_picking_return_invoicing', 'sale_stock'),
    # OCA/account-financial-reporting
    ('account_journal_report', 'account_financial_report_qweb'),
    # OCA/e-commerce
    ('website_sale_b2c', 'sale'),  # used groups are in sale
    # OCA/sale-workflow
    ('sale_order_back2draft', 'sale'),
    # OCA/social
    ('mass_mailing_security_group', 'mass_mailing'),
    # OCA/stock-logistics-workflow
    ('stock_scrap', 'stock'),
    # OCA/web
    ('web_easy_switch_company', 'web'),
]

renamed_models = {
}
