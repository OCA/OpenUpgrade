""" Encode any known changes to the database here
to help the matching process
"""

renamed_modules = {
    # This is a list of tuples (old module name, new module name)
    'account_coda': 'l10n_be_coda',
    'base_crypt': 'auth_crypt',
    'mrp_subproduct': 'mrp_byproduct',
    'users_ldap': 'auth_ldap',
    'wiki': 'document_page',
    # mgmtsystem
    'wiki_environment_manual': 'document_page_environment_manual',
    'wiki_environmental_aspect': 'document_page_environmental_aspect',
    'wiki_quality_manual': 'document_page_quality_manual',
    'wiki_health_safety_manual': 'document_page_health_safety_manual',
    'wiki_procedure': 'document_page_procedure',
    'wiki_work_instructions': 'document_page_work_instructions',
    # l10n-spain
    'nan_account_invoice_sequence': 'l10n_es_account_invoice_sequence',
    # https://github.com/OCA/crm/tree/7.0/lettermgmt
    # this worked with 6.1 too and there's no specific 6.1 version
    'letter_mgmt_v6': 'lettermgmt',
    # https://github.com/OCA/web/pull/79
    'web_widget_classes': 'web_dom_model_classes',
}

renamed_models = {
    }
