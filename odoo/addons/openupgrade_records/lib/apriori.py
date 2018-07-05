""" Encode any known changes to the database here
to help the matching process
"""

renamed_modules = {
    # OCA/connector
    # Connector module has been unfolded in 2 modules in version 10.0:
    # connector and queue_job. We need to do this to correct upgrade both
    # modules.
    'connector': 'queue_job',
    # OCA/web
    'web_shortcuts': 'web_shortcut',
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

renamed_models = {
}
