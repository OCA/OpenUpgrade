# -*- coding: utf-8 -*-
# Copyright 2016 Sergio Teruel <sergio.teruel@tecnativa.com>
# Copyright 2017 Tecnativa - Pedro M. Baeza <pedro.baeza@tecnativa.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openupgradelib import openupgrade

column_renames = {
    'account_journal': [
        ('self_checkout_payment_method', None),
    ],
    'pos_category': [
        ('image', None),
        ('image_medium', None),
        ('image_small', None),
    ],
    'pos_config': [
        ('barcode_cashier', None),
        ('barcode_customer', None),
        ('barcode_discount', None),
        ('barcode_price', None),
        ('barcode_product', None),
        ('barcode_weight', None),
        ('iface_self_checkout', None),
    ],
    'product_template': [
        ('expense_pdt', None),
        ('income_pdt', None),
    ],
    'res_users': [
        ('ean13', None),
    ],
}


@openupgrade.migrate()
def migrate(cr, version):
    openupgrade.rename_columns(cr, column_renames)
