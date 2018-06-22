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

_portal_xmlid_renames = [
    ('website_portal_sale.portal_my_invoices', 'account.portal_my_invoices'),
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
