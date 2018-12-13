""" Encode any known changes to the database here
to help the matching process
"""

renamed_modules = {
    # Odoo
    'mrp_repair': 'repair',
    'product_extended': 'mrp_bom_cost',
}

merged_modules = {
    # Odoo
    'auth_crypt': 'base',
    'account_cash_basis_base_account': 'account',
    'account_invoicing': 'account',
    'base_vat_autocomplete': 'partner_autocomplete',
    'rating_project': 'project',
    'sale_order_dates': 'sale',
    'sale_payment': 'sale',
    'sale_service_rating': 'sale_timesheet',
    'website_quote': 'sale_quotation_builder',
    'website_rating_project': 'project',
    'website_sale_options': 'website_sale',
    'website_sale_stock_options': 'website_sale_stock',
}

renamed_models = {
    # Odoo
    'procurement.rule': 'stock.rule',
    'hr.holidays': 'hr.leave',
    'hr.holidays.status': 'hr.leave.type',
    'sale.quote.template': 'sale.order.template',
    'sale.quote.option': 'sale.order.template.option',
    'sale.quote.line': 'sale.order.template.line',
    'stock.incoterms': 'account.incoterms',
}
