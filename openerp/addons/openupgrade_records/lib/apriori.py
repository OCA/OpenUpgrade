""" Encode any known changes to the database here
to help the matching process
"""

renamed_modules = {
    'account_coda': 'l10n_be_coda',
    'base_crypt': 'auth_crypt',
    'mrp_subproduct': 'mrp_byproduct',
    'users_ldap': 'auth_ldap',
    'wiki': 'document_page',
    # https://github.com/OCA/crm/tree/7.0/lettermgmt
    # this worked with 6.1 too and there's no specific 6.1 version
    'letter_mgmt_v6': 'lettermgmt',
    }

renamed_models = {
    }
