# -*- coding: utf-8 -*-
# © 2016 Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade


column_renames = {
    'product_product': [
        ('purchase_requisition', None),
    ],
}


@openupgrade.migrate()
def migrate(cr, version):
    openupgrade.rename_columns(cr, column_renames)
