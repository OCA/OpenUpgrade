# -*- coding: utf-8 -*-
# Copyright 2017 Eficent <http://www.eficent.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade

column_copies = {
    'payment_acquirer': [
        ('auto_confirm', None, None),
    ],
}

xmlids_renames = [
    ('payment_adyen.payment_acquirer_adyen',
     'payment.payment_acquirer_adyen'),
    ('payment_authorize.payment_acquirer_authorize',
     'payment.payment_acquirer_authorize'),
    ('payment_buckaroo.payment_acquirer_buckaroo',
     'payment.payment_acquirer_buckaroo'),
    ('payment_ogone.payment_acquirer_ogone',
     'payment.payment_acquirer_ogone'),
    ('payment_paypal.payment_acquirer_paypal',
     'payment.payment_acquirer_paypal'),
    ('payment_sips.payment_acquirer_sips',
     'payment.payment_acquirer_sips'),
    ('payment_transfer.payment_acquirer_transfer',
     'payment.payment_acquirer_transfer'),
]


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.copy_columns(env.cr, column_copies)
    openupgrade.rename_xmlids(env.cr, xmlids_renames)
