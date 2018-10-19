""" Encode any known changes to the database here
to help the matching process
"""

renamed_modules = {
    # Odoo
    'base_action_rule': 'base_automation',
    'crm_project_issue': 'crm_project',
    'stock_picking_wave': 'stock_picking_batch',
    'website_issue': 'website_form_project',
    'website_rating_project_issue': 'website_rating_project',
    # OCA/account-invoice-reporting
    'invoice_comment_template': 'account_invoice_comment_template',
    # OCA/credit-control
    'partner_financial_risk': 'account_financial_risk',
    'partner_payment_return_risk': 'account_payment_return_financial_risk',
    'partner_sale_risk': 'sale_financial_risk',
    # OCA/account-payment
    'account_due_list_aging_comments': 'account_due_list_aging_comment',
    # OCA/partner-contact
    'partner_sector': 'partner_industry_secondary',
    'res_partner_affiliate': 'partner_affiliate',
    # OCA/stock-logistics-reporting
    'stock_valued_picking_report': 'stock_picking_report_valued',
    # OCA/hr
    'hr_public_holidays': 'hr_holidays_public',
    # OCA/vertical-association
    'membership_prorrate': 'membership_prorate',
    'membership_prorrate_variable_period': (
        'membership_prorate_variable_period'
    ),
    # OCA/web
    'web_advanced_search_x2x': 'web_advanced_search',
}

merged_modules = {
    # Odoo
    'account_tax_cash_basis': 'account',
    'portal_gamification': 'gamification',
    'portal_stock': 'portal',
    'procurement': 'stock',
    'project_issue': 'project',
    'project_issue_sheet': 'hr_timesheet',
    'report': 'base',
    'web_calendar': 'web',
    'web_kanban': 'web',
    'website_portal': 'website',
    'website_portal_sale': 'sale_payment',
    'website_project': 'project',
    'website_project_issue': 'project',
    'website_project_timesheet': 'hr_timesheet',
    # OCA/account-invoice-reporting
    'product_brand_invoice_report': 'product_brand',
    # OCA/account-financial-reporting
    # Done here for avoiding problems if updating from a previous version
    # where account_financial_report exists as other kind of module
    'account_financial_report_qweb': 'account_financial_report',
    # OCA/bank-payment
    'portal_payment_mode': 'account_payment_mode',
    # OCA/crm
    'crm_lead_website': 'crm',
    # OCA/hr-timesheet
    'hr_timesheet_sheet_week_start_day': 'hr_timesheet_sheet',
    # OCA/product-variant
    'product_variant_supplierinfo': 'product',
    # OCA/project
    'project_issue_timesheet_time_control': 'project_timesheet_time_control',
    # OCA/sale-reporting
    'product_brand_sale_report': 'product_brand',
    'sale_proforma_report': 'sale',
    # OCA/stock-logistics-workflow
    'stock_picking_transfer_lot_autoassign': 'stock_pack_operation_auto_fill',
    # OCA/web
    'web_widget_domain_v11': 'web',
    # OCA/website
    'website_seo_redirection': 'website',
}

renamed_models = {
    'base.action.rule': 'base.automation',
    'base.action.rule.lead.test': 'base.automation.lead.test',
    'base.action.rule.line.test': 'base.automation.line.test',
    'ir.actions.report.xml': 'ir.actions.report',
    'stock.pack.operation': 'stock.move.line',
    'stock.picking.wave': 'stock.picking.batch',
}
