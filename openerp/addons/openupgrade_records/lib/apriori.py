""" Encode any known changes to the database here
to help the matching process
"""

renamed_modules = {
    # OCA/product-attribute
    'product_m2m_categories': 'product_multi_category',
    # OCA/e-commerce
    'product_links': 'product_multi_link',
    # OCA/sale-workflow
    'sale_exceptions': 'sale_exception',
    # OCA/partner-contact
    'partner_external_maps': 'partner_external_map',
    # OCA/server-tools
    'disable_openerp_online': 'disable_odoo_online',
    # OCA/runbot-addons
    'runbot_secure': 'runbot_relative',
}

renamed_models = {
}
