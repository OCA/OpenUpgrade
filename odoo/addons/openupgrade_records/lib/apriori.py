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
}

merged_modules = {
    # Odoo
    'account_tax_cash_basis': 'account',
    'portal_gamification': 'gamification',
    'portal_stock': 'stock',
    'report': 'base',
    'web_calendar': 'web',
    'web_kanban': 'web',
    'website_portal': 'website',
    'website_project': 'project',
    'website_project_timesheet': 'hr_timesheet',
}

renamed_models = {
    'base.action.rule': 'base.automation',
    'base.action.rule.lead.test': 'base.automation.lead.test',
    'base.action.rule.line.test': 'base.automation.line.test',
    'ir.actions.report.xml': 'ir.actions.report',
    'stock.pack.operation': 'stock.move.line',
    'stock.picking.wave': 'stock.picking.batch',
}
