""" Encode any known changes to the database here
to help the matching process
"""

renamed_modules = {
    # Odoo
    'crm_reveal': 'crm_iap_lead',
    'document': 'attachment_indexation',
    'payment_ogone': 'payment_ingenico',
    # OCA/...
}

merged_modules = {
    # Odoo
    'account_cancel': 'account',
    'account_voucher': 'account',
    'crm_phone_validation': 'crm',
    'decimal_precision': 'base',
    'delivery_hs_code': 'delivery',
    'hw_scale': 'hw_drivers',
    'hw_scanner': 'hw_drivers',
    'hw_screen': 'hw_drivers',
    'l10n_fr_certification': 'account',
    'l10n_fr_sale_closing': 'l10n_fr',
    'mrp_bom_cost': 'mrp_account',
    'mrp_byproduct': 'mrp',
    'payment_stripe_sca': 'payment_stripe',
    'stock_zebra': 'stock',
    'survey_crm': 'survey',
    'test_pylint': 'test_lint',
    'web_settings_dashboard': 'base_setup',
    'website_crm_phone_validation': 'website_crm',
    'website_sale_link_tracker': 'website_sale',
    'website_survey': 'survey',
    # OCA/account-reconcile
    'account_set_reconcilable': 'account',
    # OCA/social
    'mass_mailing_unique': 'mass_mailing',
    # OCA/timesheet
    'sale_timesheet_existing_project': 'sale_timesheet',
    # OCA/web
    'web_favicon': 'base',
    'web_widget_color': 'web',
}

# only used here for openupgrade_records analysis:
renamed_models = {
    # Odoo
    'account.register.payments': 'account.payment.register',
    'crm.reveal.industry': 'crm.iap.lead.industry',
    'crm.reveal.role': 'crm.iap.lead.role',
    'crm.reveal.seniority': 'crm.iap.lead.seniority',
    'mail.blacklist.mixin': 'mail.thread.blacklist',
    'mail.mail.statistics': 'mailing.trace',
    'mail.mail.statistics.report': 'mailing.trace.report',
    'mail.mass_mailing': 'mailing.mailing',
    'mail.mass_mailing.contact': 'mailing.contact',
    'mail.mass_mailing.list': 'mailing.list',
    'mail.mass_mailing.list.merge': 'mailing.list.merge',
    'mail.mass_mailing.list_contact_rel': 'mailing.contact.subscription',
    'mail.mass_mailing.stage': 'utm.stage',
    'mail.mass_mailing.tag': 'utm.tag',
    'mrp.subproduct': 'mrp.bom.byproduct',
    'sms.send_sms': 'sms.composer',
    'stock.fixed.putaway.strat': 'stock.putaway.rule',
    'report.stock.forecast': 'report.stock.quantity',
    'survey.mail.compose.message': 'survey.invite',
    'website.redirect': 'website.rewrite',
    # OCA/...
}

# only used here for openupgrade_records analysis:
merged_models = {
    # Odoo
    'account.invoice': 'account.move',
    'account.invoice.line': 'account.move.line',
    'account.invoice.tax': 'account.move.line',
    'account.voucher': 'account.move',
    'account.voucher.line': 'account.move.line',
    'lunch.order.line': 'lunch.order',
    'mail.mass_mailing.campaign': 'utm.campaign',
    'slide.category': 'slide.slide',
    'survey.page': 'survey.question',
    # OCA/...
}
