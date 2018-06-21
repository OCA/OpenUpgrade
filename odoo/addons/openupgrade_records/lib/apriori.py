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
    # OCA/credit-control
    'partner_financial_risk': 'account_financial_risk',
    'partner_payment_return_risk': 'account_payment_return_financial_risk',
    'partner_sale_risk': 'sale_financial_risk',
    # OCA/vertical-association
    'membership_prorrate': 'membership_prorate',
}

merged_modules = {
    # Odoo
    'account_tax_cash_basis': 'account',
    'portal_gamification': 'gamification',
    'portal_stock': 'portal',
    'procurement': 'stock',
    'project_issue': 'project',
    'report': 'base',
    'web_calendar': 'web',
    'web_kanban': 'web',
    'website_portal': 'website',
    'website_project': 'project',
    'website_project_timesheet': 'hr_timesheet',
    'website_sale_stock_control': 'stock',
    # OCA/account-financial-reporting
    # Done here for avoiding problems if updating from a previous version
    # where account_financial_report exists as other kind of module
    'account_financial_report_qweb': 'account_financial_report',
    # OCA/bank-payment
    'portal_payment_mode': 'account_payment_mode',
    # OCA/stock-logistics-workflow
    'stock_picking_transfer_lot_autoassign': 'stock_pack_operation_auto_fill',
}

renamed_models = {
    'base.action.rule': 'base.automation',
    'base.action.rule.lead.test': 'base.automation.lead.test',
    'base.action.rule.line.test': 'base.automation.line.test',
    'ir.actions.report.xml': 'ir.actions.report',
    'stock.pack.operation': 'stock.move.line',
    'stock.picking.wave': 'stock.picking.batch',
}
