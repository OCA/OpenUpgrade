""" Encode any known changes to the database here
to help the matching process
"""

renamed_modules = {
    # OCA/product-attribute
    'product_m2m_categories': 'product_multi_category',
    # OCA/e-commerce
    'product_links': 'product_multi_link',
    # OCA/sale-workflow
    'sale_exceptions': 'sale_exception',
    # OCA/partner-contact
    'partner_external_maps': 'partner_external_map',
    'partner_relations': 'partner_multi_relation',
    # OCA/server-tools
    'disable_openerp_online': 'disable_odoo_online',
    'inactive_session_timeout': 'auth_session_timeout',
    # OCA/runbot-addons
    'runbot_secure': 'runbot_relative',
    # not exactly a module rename, but they do the same
    'account_check_writing': 'account_check_printing',
    # same here, whoever want this will also need bank-payment
    'account_payment': 'account_payment_order',
    # OCA/account-invoicing
    'account_refund_original': 'account_invoice_refund_link',
    # OCA/social
    'marketing_security_group': 'mass_mailing_security_group',
    # odoomrp/odoomrp-wip
    'product_variants_no_automatic_creation': 'product_variant_configurator',
    'sale_product_variants': 'sale_variant_configurator',
    'sale_stock_product_variants': 'sale_stock_variant_configurator',
    'purchase_product_variants': 'purchase_variant_configurator',
    # OCA/account-payment - Module merged in OCA/account-financial-tools
    'account_payment_term_multi_day': 'account_payment_term_extension',
    # OCA/account-financial-reporting
    'account_financial_report_webkit': 'account_financial_report_qweb',
    # OCA/contract
    'account_analytic_analysis': 'contract',
    'contract_recurring_plans': 'contract_recurring_analytic_distribution',
    # OCA/website
    'website_disable_odoo': 'website_odoo_debranding',
    # OCA/account-analytic
    'account_analytic_plans': 'account_analytic_distribution',
    'account_analytic_plan_required': 'account_analytic_distribution_required',
    'sale_analytic_plans': 'sale_analytic_distribution',
    'purchase_analytic_plans': 'purchase_analytic_distribution',
    # OCA/hr
    'hr_expense_analytic_plans': 'hr_expense_analytic_distribution',
    # OCA/project
    'project_work_time_control': 'project_timesheet_time_control',
}

renamed_models = {
}
