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
    # OCA/bank-statement-import
    'account_banking': 'account_bank_statement_import',
    'account_banking_camt': 'bank_statement_parse_camt',
    'account_banking_nl_ing_mt940': 'bank_statement_parse_nl_ing_mt940',
    'account_banking_nl_rabo_mt940': 'bank_statement_parse_nl_rabo_mt940',
}

renamed_models = {
}
