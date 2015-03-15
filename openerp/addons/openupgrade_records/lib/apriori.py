""" Encode any known changes to the database here
to help the matching process
"""

renamed_modules = {
    'base_calendar': 'calendar',
    'mrp_jit': 'procurement_jit',
    # OCA/account-invoicing
    'invoice_validation_wkfl': 'account_invoice_validation_workflow',
    # OCA/server-tools
    'audittrail': 'auditlog',
}

renamed_models = {
}
