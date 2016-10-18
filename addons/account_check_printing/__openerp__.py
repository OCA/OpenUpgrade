# -*- coding: utf-8 -*-
{
    'name': 'Check Printing Base',
    'version': '1.0',
    'category': 'Accounting',
    'summary': 'Check printing commons',
    'description': """
This module offers the basic functionalities to make payments by printing checks.
It must be used as a dependency for modules that provide country-specific check templates.
The check settings are located in the accounting journals configuration page.

OpenUpgrade specific: we set account_voucher here as a dependency for
account_check_printing. account_voucher was an actual dependency for
account_check_writing in 8.0. Therefore, when upgrading this module, we can
be sure account_voucher is also installed. But we have to make sure
account_voucher is loaded before account_check_printing, because the migration
of check information uses the results of account_voucher migration. To be
specific: the account_payment records created by account_voucher migration.
    """,
    'website': 'https://www.odoo.com/page/accounting',
    'depends' : [
        'account',
        'account_voucher',  # Not for normal Odoo, but needed for migration
    ],
    'data': [
        'data/check_printing.xml',
        'views/account_journal_dashboard_view.xml',
        'views/account_journal_view.xml',
        'views/account_payment_view.xml',
        'wizard/print_pre_numbered_checks.xml'
    ],
    'installable': True,
    'auto_install': False,
}
