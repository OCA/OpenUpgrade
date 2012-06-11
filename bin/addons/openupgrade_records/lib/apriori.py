""" Encode any known changes to the database here
to help the matching process
"""

renamed_modules = {
    'association_profile': 'association',
    'report_analytic_planning': 'project_planning',
    }

renamed_models = {
    'mrp.procurement': 'procurement.order',
    }
