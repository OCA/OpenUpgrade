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

renamed_models = {
}
