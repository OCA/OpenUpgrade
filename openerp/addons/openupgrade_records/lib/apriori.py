""" Encode any known changes to the database here
to help the matching process
"""

renamed_modules = {
    'base_calendar': 'calendar',
    'mrp_jit': 'procurement_jit',
    'project_mrp': 'sale_service',
    # OCA/account-invoicing
    'invoice_validation_wkfl': 'account_invoice_validation_workflow',
    'account_invoice_zero': 'account_invoice_zero_autopay',
    # OCA/server-tools
    'audittrail': 'auditlog',
    # OCA/bank-statement-import
    'account_banking': 'account_bank_statement_import',
    'account_banking_camt': 'account_bank_statement_import_camt',
    'account_banking_mt940':
        'account_bank_statement_import_mt940_base',
    'account_banking_nl_ing_mt940':
        'account_bank_statement_import_mt940_nl_ing',
    'account_banking_nl_rabo_mt940':
        'account_bank_statement_import_mt940_nl_rabo',
}

renamed_models = {
}
