# -*- coding: utf-8 -*-
# Copyright 2017 bloopark systems (<http://bloopark.de>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade


# backup of state column with old / non existing values 'proforma' and
# 'proforma2'
column_copies = {
    'account_invoice': [
        ('state', None, None),
    ],
}

# It comes from the renaming of website_portal_sale > sale_payment
_portal_xmlid_renames = [
    ('sale_payment.portal_my_invoices', 'account.portal_my_invoices'),
]

# It comes from the renaming of portal_sale > sale
_portal_sale_xmlid_renames = [
    ('sale.portal_account_invoice_user_rule',
     'account.account_invoice_rule_portal'),
    ('sale.portal_account_invoice_line_rule',
     'account.account_invoice_line_rule_portal'),
]


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.copy_columns(env.cr, column_copies)
    # account_tax_cash_basis was merged with account, so there is no module
    # entry anymore to check if it was installed. Check one of its columns
    # instead.
    if openupgrade.column_exists(env.cr, 'account_tax', 'use_cash_basis'):
        openupgrade.rename_columns(
            env.cr, {'account_tax': [('use_cash_basis', None)]})
    openupgrade.delete_record_translations(env.cr, 'account', [
        'mail_template_data_notification_email_account_invoice',
        'email_template_edi_invoice'
    ])
    openupgrade.rename_xmlids(env.cr, _portal_xmlid_renames)
    openupgrade.rename_xmlids(env.cr, _portal_sale_xmlid_renames)
    openupgrade.add_fields(
        env, [
            ('price_total', 'account.invoice.line', 'account_invoice_line',
             'monetary', False, 'account'),
            ('tax_base_amount', 'account.move.line', 'account_move_line',
             'monetary', False, 'account'),
        ]
    )
