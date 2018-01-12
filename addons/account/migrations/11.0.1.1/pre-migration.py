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


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.copy_columns(env.cr, column_copies)
    openupgrade.delete_record_translations(env.cr, 'account', [
        'mail_template_data_notification_email_account_invoice',
        'email_template_edi_invoice'
    ])
