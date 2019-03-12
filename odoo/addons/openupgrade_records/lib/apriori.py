""" Encode any known changes to the database here
to help the matching process
"""

renamed_modules = {
    # Odoo
    'mrp_repair': 'repair',
    'product_extended': 'mrp_bom_cost',
    # OCA/community-data-files
    'product_uom_unece': 'uom_unece',
}

merged_modules = {
    # Odoo
    'auth_crypt': 'base',
    'account_cash_basis_base_account': 'account',
    'account_invoicing': 'account',
    'base_vat_autocomplete': 'partner_autocomplete',
    'product_extended': 'mrp_bom_cost',
    'rating_project': 'project',
    'sale_order_dates': 'sale',
    'sale_payment': 'sale',
    'sale_service_rating': 'sale_timesheet',
    'web_planner': 'web',
    'website_form_metadata': 'website_form',
    'website_quote': 'sale_quotation_builder',
    'website_rating_project': 'project',
    'website_sale_options': 'website_sale',
    'website_sale_stock_options': 'website_sale_stock',
    # OCA/account-financial-tools
    'account_reversal': 'account',
    # OCA/server-auth
    'auth_brute_force': 'base',
    # OCA/web
    'web_no_bubble': 'web',
    'web_sheet_full_width': 'web_responsive',
}

renamed_models = {
    # Odoo
    'hr.holidays': 'hr.leave',
    'hr.holidays.status': 'hr.leave.type',
    'mrp.repair': 'repair.order',
    'mrp.repair.fee': 'repair.fee',
    'mrp.repair.line': 'repair.line',
    'procurement.rule': 'stock.rule',
    'product.attribute.line': 'product.template.attribute.line',
    'product.attribute.price': 'product.template.attribute.value',
    'product.uom': 'uom.uom',
    'product.uom.categ': 'uom.category',
    'sale.quote.line': 'sale.order.template.line',
    'sale.quote.option': 'sale.order.template.option',
    'sale.quote.template': 'sale.order.template',
    'stock.incoterms': 'account.incoterms',
    # 'stock.location.path': 'stock.rule',
}
