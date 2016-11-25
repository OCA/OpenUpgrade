# -*- coding: utf-8 -*-
# © 2016 Tecnativa - <vicent.cubells@tecnativa.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade

column_renames = {
    'payment_acquirer': [
        ('validation', None),
    ],
    'payment_transaction': [
        ('date_create', None),
        ('partner_reference', None),
    ],
}


@openupgrade.migrate()
def migrate(cr, version):
    openupgrade.rename_columns(cr, column_renames)
