""" Encode any known changes to the database here
to help the matching process
"""

# Renamed modules is a mapping from old module name to new module name
renamed_modules = {
    # odoo
    "account_facturx": "account_edi_facturx",
    "website_rating": "portal_rating",
    # OCA/server-tools
    "openupgrade_records": "upgrade_analysis",
    # OCA/...
}

# Merged modules contain a mapping from old module names to other,
# preexisting module names
merged_modules = {
    # odoo
    "account_analytic_default": "account",
    "account_analytic_default_hr_expense": "hr_expense",
    "account_analytic_default_purchase": "purchase",
    "hr_expense_check": "hr_expense",
    "hr_holidays_calendar": "hr_holidays",
    "hw_proxy": "hw_drivers",
    "l10n_cn_small_business": "l10n_cn",
    "partner_autocomplete_address_extended": "base_address_extended",
    "pos_cash_rounding": "point_of_sale",
    "pos_kitchen_printer": "pos_restaurant",
    "pos_reprint": "point_of_sale",
    "website_theme_install": "website",
    # OCA/partner-contact
    "partner_bank_active": "base",
    # OCA/...
}

# only used here for upgrade_analysis
renamed_models = {
    # odoo
    "email_template.preview": "mail.template.preview",
    "event.answer": "event.question.answer",
    "product.style": "product.ribbon",
    "survey.user_input_line": "survey.user_input.line",
    # OCA/server-tools
    "openupgrade.analysis.wizard": "upgrade.analysis",
    "openupgrade.attribute": "upgrade.attribute",
    "openupgrade.comparison.config": "upgrade.comparison.config",
    "openupgrade.record": "upgrade.record",
    "openupgrade.generate.records.wizard": "upgrade.generate.record.wizard",
    "openupgrade.install.all.wizard": "upgrade.install.wizard",
}

# only used here for upgrade_analysis
merged_models = {}
